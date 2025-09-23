import os
import socket
import struct
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.management.commands.f1_2025_mappings import DRIVERS_2025, TEAMS_2025, TRACKS_2025
from apps.core.models.live import LiveSession, LiveLap, LiveTelemetryPoint


# =========================
#   2025 SPEC CONSTANTS
# =========================

# struct PacketHeader (little-endian), 29 bytes:
# uint16 m_packetFormat;  // 2025
# uint8  m_gameYear, m_gameMajorVersion, m_gameMinorVersion, m_packetVersion, m_packetId;
# uint64 m_sessionUID;
# float  m_sessionTime;
# uint32 m_frameIdentifier, m_overallFrameIdentifier;
# uint8  m_playerCarIndex, m_secondaryPlayerCarIndex;
HEADER_STRUCT = struct.Struct("<H5B Q f I I 2B")
HEADER_SIZE = HEADER_STRUCT.size  # 29

# Packet IDs (F1 25)
PACKET_MOTION               = 0
PACKET_SESSION              = 1
PACKET_LAP_DATA             = 2
PACKET_EVENT                = 3
PACKET_PARTICIPANTS         = 4
PACKET_CAR_SETUPS           = 5
PACKET_CAR_TELEMETRY        = 6
PACKET_CAR_STATUS           = 7
PACKET_FINAL_CLASSIFICATION = 8
PACKET_LOBBY_INFO           = 9
PACKET_CAR_DAMAGE           = 10
PACKET_SESSION_HISTORY      = 11
PACKET_TYRE_SETS            = 12
PACKET_MOTION_EX            = 13
PACKET_TIME_TRIAL           = 14
PACKET_LAP_POSITIONS        = 15

# LapData: 29(header) + 22 * stride + 2 = 1285 → stride = 57
LAPDATA_STRIDE = 57
LAP_LAST_MS_OFF = 0   # uint32 m_lastLapTimeInMS
LAP_CUR_MS_OFF  = 4   # uint32 m_currentLapTimeInMS
# m_currentLapNum шукаємо евристично — див. safe_extract_lapnum()

# CarTelemetry: 29 + 22 * 60 + 3 = 1352 → stride = 60
CTELE_STRIDE    = 60
CTL_SPEED_OFF   = 0   # uint16 m_speed
CTL_THROTTLE_OFF= 2   # float  m_throttle (0..1)
CTL_BRAKE_OFF   = 10  # float  m_brake    (0..1)
CTL_GEAR_OFF    = 15  # int8   m_gear
CTL_RPM_OFF     = 16  # uint16 m_engineRPM


# =========================
#   HELPERS
# =========================

def safe_unpack_header(buf: bytes):
    if len(buf) < HEADER_SIZE:
        return None, None, None
    try:
        (_packet_format,
         _gy, _gmaj, _gmin, _pver, packet_id,
         session_uid,
         _sess_time,
         _frame_id, _overall_frame_id,
         player_car_index, _secondary_idx) = HEADER_STRUCT.unpack_from(buf, 0)
        return session_uid, packet_id, player_car_index
    except Exception:
        return None, None, None


def safe_extract_lapnum(entry_bytes: bytes) -> int:
    candidates = [34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56]
    for off in candidates:
        if len(entry_bytes) <= off:
            continue
        val = struct.unpack_from("<B", entry_bytes, off)[0]
        if 1 <= val <= 200:
            return val
    return 0


def extract_player_lapdata(buf: bytes, player_index: int):
    base = HEADER_SIZE + player_index * LAPDATA_STRIDE
    end  = base + LAPDATA_STRIDE
    if len(buf) < end:
        return {"currentLapNum": 0, "currentLapTimeMs": 0, "lastLapTimeMs": None}

    entry   = memoryview(buf)[base:end]
    last_ms = struct.unpack_from("<I", entry, LAP_LAST_MS_OFF)[0]
    cur_ms  = struct.unpack_from("<I", entry, LAP_CUR_MS_OFF)[0]
    cur_no  = safe_extract_lapnum(entry.tobytes())

    return {
        "currentLapNum": int(cur_no),
        "currentLapTimeMs": int(cur_ms),
        "lastLapTimeMs": int(last_ms) if last_ms else None,
    }


def extract_player_telemetry(buf: bytes, player_index: int):
    base = HEADER_SIZE + player_index * CTELE_STRIDE
    end  = base + CTELE_STRIDE
    if len(buf) < end:
        return {"speedKmh": 0.0, "rpm": 0, "throttlePct": 0.0, "brakePct": 0.0, "gear": 0}

    speed    = struct.unpack_from("<H", buf, base + CTL_SPEED_OFF)[0]
    throttle = struct.unpack_from("<f", buf, base + CTL_THROTTLE_OFF)[0] * 100.0
    brake    = struct.unpack_from("<f", buf, base + CTL_BRAKE_OFF)[0] * 100.0
    gear     = struct.unpack_from("<b", buf, base + CTL_GEAR_OFF)[0]
    rpm      = struct.unpack_from("<H", buf, base + CTL_RPM_OFF)[0]

    return {
        "speedKmh": float(speed),
        "rpm": int(rpm),
        "throttlePct": float(throttle),
        "brakePct": float(brake),
        "gear": int(gear),
    }


def apply_classification_or_history(session: LiveSession, buf: bytes):
    pass


# =========================
#   DJANGO COMMAND
# =========================

class Command(BaseCommand):
    help = "Listen Codemasters F1 25 UDP and store live laps."

    def add_arguments(self, parser):
        parser.add_argument("--host", default="0.0.0.0")
        parser.add_argument("--port", type=int, default=20777)
        parser.add_argument("--push-ws", action="store_true", default=False,
                            help="Broadcast telemetry via Channels group 'live_telemetry'")
        parser.add_argument("--debug", action="store_true", default=False,
                            help="Print packet counters and header details")

    def handle(self, *args, **opts):
        host = opts["host"]
        port = opts["port"]
        debug = bool(opts.get("debug", False))

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        sock.settimeout(2.0)
        self.stdout.write(self.style.SUCCESS(f"Listening UDP on {host}:{port}"))

        # Поточний стан у процесі
        current_sessions = {}  # sid (str)                -> LiveSession
        last_lap_num     = {}  # sid (str)                -> int
        prev_cur_ms      = {}  # sid (str)                -> int
        prev_last_ms     = {}  # sid (str)                -> int
        lap_start_ms     = {}  # sid (str)                -> epoch ms
        current_laps     = {}  # (sid, lap_number)        -> LiveLap

        pkt_cnt = 0
        by_id = {i: 0 for i in range(0, 16)}

        while True:
            try:
                data, _ = sock.recvfrom(4096)
            except socket.timeout:
                continue
            except Exception as e:
                self.stderr.write(f"Socket error (recv): {e}")
                continue

            pkt_cnt += 1

            # ---- Header ----
            session_uid, packet_id, player_index = safe_unpack_header(data)
            if session_uid is None:
                if debug:
                    self.stderr.write("[DEBUG] bad/short header, skip packet")
                continue


            sid = str(session_uid)

            session = current_sessions.get(sid)
            if session is None:
                session = LiveSession.objects.filter(session_uid=sid).first()
                if session is None:
                    try:
                        session = LiveSession.objects.create(
                            session_uid=sid,
                            car_label="—",
                            driver_label="—",
                            track_label="—",
                        )
                    except Exception:
                        session = LiveSession.objects.get(session_uid=sid)

                current_sessions[sid] = session
                last_lap_num.setdefault(sid, 0)
                prev_cur_ms.setdefault(sid, 0)
                prev_last_ms.setdefault(sid, 0)
                lap_start_ms.setdefault(sid, int(time.time() * 1000))


            if packet_id == PACKET_LAP_DATA:
                lapd = extract_player_lapdata(data, player_index)
                cur_lap_num = int(lapd.get("currentLapNum") or 0)
                cur_ms      = int(lapd.get("currentLapTimeMs") or 0)
                last_ms     = int(lapd.get("lastLapTimeMs") or 0)

                prev_num  = last_lap_num.get(sid, 0)
                prev_cur  = prev_cur_ms.get(sid, 0)
                prev_last = prev_last_ms.get(sid, 0)

                new_lap_detected = False

                if cur_lap_num > prev_num:
                    new_lap_detected = True
                elif last_ms and last_ms != prev_last:
                    new_lap_detected = True
                elif cur_ms < prev_cur and prev_cur > 2000:
                    new_lap_detected = True

                if new_lap_detected:
                    if prev_num > 0:
                        ll_prev = current_laps.get((sid, prev_num))
                        if ll_prev and last_ms and not ll_prev.lap_time_ms:
                            ll_prev.lap_time_ms = last_ms
                            ll_prev.save()

                    next_num = cur_lap_num if cur_lap_num > 0 else prev_num + 1
                    ll = LiveLap.objects.create(session=session, lap_number=next_num)
                    current_laps[(sid, next_num)] = ll
                    last_lap_num[sid] = next_num
                    lap_start_ms[sid] = int(time.time() * 1000)

                prev_cur_ms[sid]  = cur_ms
                prev_last_ms[sid] = last_ms

                if debug:
                    self.stdout.write(
                        f"[LAP] curLapNum={cur_lap_num} cur_ms={cur_ms} last_ms={last_ms} "
                        f"storedLap={last_lap_num[sid]} new={new_lap_detected}"
                    )

            elif packet_id == PACKET_PARTICIPANTS:
                try:
                    if len(data) < HEADER_SIZE + 1:
                        raise ValueError("participants packet too short")

                    num_active = struct.unpack_from("<B", data, HEADER_SIZE)[0]
                    base = HEADER_SIZE + 1
                    stride = 56

                    if 0 <= player_index < num_active:
                        entry = base + player_index * stride
                        driver_id = struct.unpack_from("<B", data, entry + 1)[0]
                        team_id   = struct.unpack_from("<B", data, entry + 3)[0]
                        raw_name  = struct.unpack_from("48s", data, entry + 7)[0]
                        name_str  = raw_name.split(b"\x00", 1)[0].decode("utf-8", errors="ignore").strip()

                        driver_name = name_str or DRIVERS_2025.get(driver_id, f"Driver {driver_id}")
                        team_name   = TEAMS_2025.get(team_id, f"Team {team_id}")

                        changed = False
                        if session.driver_label != driver_name:
                            session.driver_label = driver_name
                            changed = True
                        if session.car_label != team_name:
                            session.car_label = team_name
                            changed = True
                        if changed:
                            session.save(update_fields=["driver_label", "car_label"])
                            if debug:
                                self.stdout.write(
                                    f"[PARTICIPANTS] driver={driver_name} (id={driver_id}) team={team_name} (id={team_id})"
                                )
                except Exception as e:
                    if debug:
                        self.stderr.write(f"[PARTICIPANTS] parse error: {e}")

            elif packet_id == PACKET_CAR_TELEMETRY:
                tel = extract_player_telemetry(data, player_index)

                cur_no = last_lap_num.get(sid, 0)
                ll = current_laps.get((sid, cur_no))
                if ll:
                    now_ms = int(time.time() * 1000)
                    t_ms = now_ms - lap_start_ms[sid]
                    try:
                        LiveTelemetryPoint.objects.create(
                            lap=ll,
                            t_ms=t_ms,
                            speed_kmh=tel["speedKmh"],
                            rpm=tel.get("rpm"),
                            throttle=tel.get("throttlePct"),
                            brake=tel.get("brakePct"),
                            gear=tel.get("gear"),
                        )
                    except Exception as db_e:
                        if debug:
                            self.stderr.write(f"[DB] telemetry insert error: {db_e}")

                    if debug and pkt_cnt % 50 == 0:
                        self.stdout.write(f"[TEL→DB] lap={cur_no} t={t_ms}ms v={tel['speedKmh']:.0f}")

            elif packet_id == PACKET_SESSION:
                try:
                    possible_offsets = [HEADER_SIZE + 5, HEADER_SIZE + 6, HEADER_SIZE + 8, HEADER_SIZE + 10]
                    track_id = None
                    for off in possible_offsets:
                        if len(data) > off:
                            val = struct.unpack_from("<B", data, off)[0]
                            if 0 <= val <= 60:
                                track_id = val
                                break
                    if track_id is not None:
                        track_name = TRACKS_2025.get(track_id, f"Track {track_id}")
                        if session.track_label != track_name:
                            session.track_label = track_name
                            session.save(update_fields=["track_label"])
                            if debug:
                                self.stdout.write(f"[SESSION] track={track_name} (id={track_id})")
                except Exception as e:
                    if debug:
                        self.stderr.write(f"[SESSION] parse error: {e}")

            elif packet_id in (PACKET_FINAL_CLASSIFICATION, PACKET_SESSION_HISTORY):
                apply_classification_or_history(session, data)
                session.finished_at = timezone.now()
                session.save()
