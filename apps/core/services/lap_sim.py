from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class SimResult:
    lap_time_sec: float
    lap_time_str: str
    points: List[Tuple[float,float]]
    full_throttle_pct: int
    heavy_braking_pct: int
    cornering_pct: int
    category: str

def format_lap_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"

def build_speed_polyline(points, w=1000, h=260, pad=40, y_min=40.0, y_max=360.0):
    n = len(points)
    if n <= 1:
        x = w / 2.0
        y = (h - pad) - ((points[0][1] - y_min) / (y_max - y_min)) * (h - 2*pad) if n == 1 else (h/2)
        return f"{x:.1f},{y:.1f}"

    span_x = (w - 2*pad) / (n - 1)
    span_y = (h - 2*pad)
    out = []
    for i, (_, v) in enumerate(points):
        v = max(y_min, min(v, y_max))
        x = pad + i * span_x
        y = (h - pad) - ((v - y_min) / (y_max - y_min)) * span_y
        out.append(f"{x:.1f},{y:.1f}")
    return " ".join(out)

def build_ticks_y(h=260, pad=40, y_min=40.0, y_max=360.0, step=40.0):
    span_y = (h - 2*pad)
    ticks = []
    value = y_min
    while value <= y_max + 1e-6:
        ratio = (value - y_min) / (y_max - y_min)
        y = (h - pad) - ratio * span_y
        ticks.append({"y": round(y, 1), "label": str(int(value))})
        value += step
    return ticks

def build_ticks_x(total_sec: float, w=1000, pad=40, parts=5):
    def fmt(t):
        m = int(t // 60); s = t % 60
        return f"{m}:{s:06.3f}"
    ticks = []
    for i in range(parts+1):
        ratio = i / parts
        x = pad + ratio * (w - 2*pad)
        ticks.append({"x": round(x, 1), "label": fmt(total_sec * ratio)})
    return ticks


def simulate_lap(length_km: float, turns: int, car_rating: int, driver_rating: int) -> SimResult:
    is_f1 = car_rating >= 11
    category = "F1" if is_f1 else "GT3"

    base_spk = 15.0 if is_f1 else 20.0
    turn_penalty = 0.15 if is_f1 else 0.25

    baseline = length_km * base_spk + turns * turn_penalty

    # Вплив рейтингу: машина важить більше (щоб 7/10 на 15/15 міг бути дуже швидким,
    # але 10/10 на 8/15 — не зможе встановити top time)
    car_norm = max(1, min(car_rating, 15)) / 15.0
    drv_norm = max(1, min(driver_rating, 10)) / 10.0
    perf = 0.75 * car_norm + 0.25 * drv_norm

    # Фактор часу: кращий perf → менше часу. Межі підібрані помірно.
    time_factor = 1.15 - 0.35 * perf
    lap_time = max(1.0, baseline * time_factor)

    CALIBRATION_SECS = {
        "F1": +10.0,
        "GT3": +10.0,
    }
    lap_time = max(1.0, lap_time + CALIBRATION_SECS["F1" if is_f1 else "GT3"])

    # Синтетична телеметрія швидкості (N точок рівномірно по часу)
    N = max(80, turns * 10)
    vmax = 330 if is_f1 else 270
    vmin = 85 if is_f1 else 70
    points = []
    for i in range(N):
        t = lap_time * i / (N - 1)
        # хвиля швидкості (синус), імітація секторів
        import math
        base_wave = (math.sin(2*math.pi * (i/N) * 3) + 1) / 2  # 0..1
        speed = vmin + (vmax - vmin) * (0.65*base_wave + 0.35)
        # додаткові падіння в "зонах" поворотів
        if turns > 0:
            for k in range(3, turns+1, max(1, turns//6 or 1)):
                center = (k / (turns+1)) * N
                width = N * 0.02
                depth = 0.25 if is_f1 else 0.32
                speed -= (vmax - vmin) * depth * math.exp(-((i-center)**2)/(2*width**2))
        # вплив перформансу
        speed *= 0.9 + 0.2 * perf
        points.append((t, max(40.0, min(speed, vmax))))

    full_throttle_pct = int(60 + 25*perf + (5 if is_f1 else -2))
    heavy_braking_pct = int(8 + (2 if is_f1 else 4))
    cornering_pct = int(10 + (2 if is_f1 else 4))

    return SimResult(
        lap_time_sec=lap_time,
        lap_time_str=format_lap_time(lap_time),
        points=points,
        full_throttle_pct=min(full_throttle_pct, 95),
        heavy_braking_pct=min(heavy_braking_pct, 25),
        cornering_pct=min(cornering_pct, 25),
        category=category,
    )
