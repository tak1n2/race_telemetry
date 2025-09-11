import datetime
import unittest
from apps.core.models.car import Car

class CarModelTests(unittest.TestCase):

    def setUp(self):
        self.car_data = {
            "type": "Formula 1",
            "maker": "Ferrari",
            "model": "SF-23",
            "year": 2023,
        }
        self.car = Car.objects.create(**self.car_data)

    def test_create_car(self):
        car = Car.objects.get(id=self.car.id)
        self.assertEqual(car.type, self.car_data["type"])
        self.assertEqual(car.maker, self.car_data["maker"])
        self.assertEqual(car.model, self.car_data["model"])
        self.assertEqual(car.year, self.car_data["year"])

    def test_update_car(self):
        self.car.model = "SF-24"
        self.car.year = 2024
        self.car.save()

        updated_car = Car.objects.get(id=self.car.id)
        self.assertEqual(updated_car.model, "SF-24")
        self.assertEqual(updated_car.year, 2024)

    def test_delete_car(self):
        car_id = self.car.id
        self.car.delete()
        with self.assertRaises(Car.DoesNotExist):
            Car.objects.get(id=car_id)

    def tearDown(self):
        Car.objects.all().delete()
