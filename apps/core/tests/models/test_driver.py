import unittest
from apps.core.models.driver import Driver
from apps.core.models.team import Team


class DriverModelTests(unittest.TestCase):

    def setUp(self):
        self.team = Team.objects.create(name="Ferrari", country="Italy")
        self.driver_data = {
            "first_name": "Charles",
            "last_name": "Leclerc",
            "number": 16,
            "country": "Monaco",
            "team": self.team,
        }
        self.driver = Driver.objects.create(**self.driver_data)

    def test_create_driver(self):
        driver = Driver.objects.get(id=self.driver.id)
        self.assertEqual(driver.first_name, self.driver_data["first_name"])
        self.assertEqual(driver.last_name, self.driver_data["last_name"])
        self.assertEqual(driver.number, self.driver_data["number"])
        self.assertEqual(driver.country, self.driver_data["country"])
        self.assertEqual(driver.team, self.team)

    def test_update_driver(self):
        self.driver.first_name = "Carlos"
        self.driver.last_name = "Sainz"
        self.driver.number = 55
        self.driver.save()

        updated_driver = Driver.objects.get(id=self.driver.id)
        self.assertEqual(updated_driver.first_name, "Carlos")
        self.assertEqual(updated_driver.last_name, "Sainz")
        self.assertEqual(updated_driver.number, 55)

    def test_delete_driver(self):
        driver_id = self.driver.id
        self.driver.delete()
        with self.assertRaises(Driver.DoesNotExist):
            Driver.objects.get(id=driver_id)

    def tearDown(self):
        Driver.objects.all().delete()
        Team.objects.all().delete()
