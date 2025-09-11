import unittest
import datetime
from apps.core.models.lap import Lap
from apps.core.models.driver import Driver
from apps.core.models.track import Track
from apps.core.models.car import Car
from apps.core.models.team import Team


class LapModelTests(unittest.TestCase):

    def setUp(self):
        self.team = Team.objects.create(name="Red Bull", country="Austria")
        self.driver = Driver.objects.create(
            first_name="Max",
            last_name="Verstappen",
            number=1,
            country="Netherlands",
            team=self.team,
        )
        self.track = Track.objects.create(
            name="Spa-Francorchamps", location="Belgium", length_km=7.004, turns=20
        )
        self.car = Car.objects.create(
            type="Formula 1", maker="Red Bull", model="RB19", year=2023
        )

        self.lap_data = {
            "lap_number": 1,
            "lap_time": datetime.time(0, 1, 45),
            "sector1_time": 32.5,
            "sector2_time": 45.2,
            "sector3_time": 27.3,
            "driver": self.driver,
            "track": self.track,
            "car": self.car,
        }
        self.lap = Lap.objects.create(**self.lap_data)

    def test_create_lap(self):
        lap = Lap.objects.get(id=self.lap.id)
        self.assertEqual(lap.lap_number, self.lap_data["lap_number"])
        self.assertEqual(lap.driver, self.driver)
        self.assertEqual(lap.track, self.track)
        self.assertEqual(lap.car, self.car)

    def test_update_lap(self):
        self.lap.lap_number = 2
        self.lap.sector1_time = 31.8
        self.lap.save()

        updated_lap = Lap.objects.get(id=self.lap.id)
        self.assertEqual(updated_lap.lap_number, 2)
        self.assertEqual(updated_lap.sector1_time, 31.8)

    def test_delete_lap(self):
        lap_id = self.lap.id
        self.lap.delete()
        with self.assertRaises(Lap.DoesNotExist):
            Lap.objects.get(id=lap_id)

    def tearDown(self):
        Lap.objects.all().delete()
        Car.objects.all().delete()
        Track.objects.all().delete()
        Driver.objects.all().delete()
        Team.objects.all().delete()
