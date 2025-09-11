import unittest
import datetime
from apps.core.models.telemetry_point import TelemetryPoint
from apps.core.models.lap import Lap
from apps.core.models.driver import Driver
from apps.core.models.track import Track
from apps.core.models.car import Car
from apps.core.models.team import Team


class TelemetryPointModelTests(unittest.TestCase):

    def setUp(self):
        self.team = Team.objects.create(name="Mercedes AMG", country="Germany")
        self.driver = Driver.objects.create(
            first_name="Lewis",
            last_name="Hamilton",
            number=44,
            country="UK",
            team=self.team,
        )
        self.track = Track.objects.create(
            name="Marina Bay", location="Singapore", length_km=4.940, turns=16
        )
        self.car = Car.objects.create(
            type="Formula 1", maker="Mercedes AMG", model="W09", year=2018
        )
        self.lap = Lap.objects.create(
            lap_number=1,
            lap_time=datetime.time(0, 1, 36),
            sector1_time=26.2,
            sector2_time=37.0,
            sector3_time=30.0,
            driver=self.driver,
            track=self.track,
            car=self.car,
        )

        self.tp_data = {
            "timestamp": datetime.time(0, 0, 15),
            "speed": 280.5,
            "rpm": 12000,
            "throttle": 95.0,
            "brake": 0.0,
            "gear": 7,
            "lap": self.lap,
        }
        self.tp = TelemetryPoint.objects.create(**self.tp_data)

    def test_create_tp(self):
        tp = TelemetryPoint.objects.get(id=self.tp.id)
        self.assertEqual(tp.speed, self.tp_data["speed"])
        self.assertEqual(tp.rpm, self.tp_data["rpm"])
        self.assertEqual(tp.throttle, self.tp_data["throttle"])
        self.assertEqual(tp.brake, self.tp_data["brake"])
        self.assertEqual(tp.gear, self.tp_data["gear"])
        self.assertEqual(tp.lap, self.lap)

    def test_update_tp(self):
        self.tp.speed = 300.0
        self.tp.gear = 8
        self.tp.save()

        updated_tp = TelemetryPoint.objects.get(id=self.tp.id)
        self.assertEqual(updated_tp.speed, 300.0)
        self.assertEqual(updated_tp.gear, 8)

    def test_delete_tp(self):
        tp_id = self.tp.id
        self.tp.delete()
        with self.assertRaises(TelemetryPoint.DoesNotExist):
            TelemetryPoint.objects.get(id=tp_id)

    def tearDown(self):
        TelemetryPoint.objects.all().delete()
        Lap.objects.all().delete()
        Car.objects.all().delete()
        Track.objects.all().delete()
        Driver.objects.all().delete()
        Team.objects.all().delete()
