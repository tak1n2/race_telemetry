import unittest
from apps.core.models.team import Team

class TeamModelTests(unittest.TestCase):

    def setUp(self):
        self.team_data = {
            "name": "Mercedes AMG",
            "country": "Germany",
        }
        self.team = Team.objects.create(**self.team_data)

    def test_create_team(self):
        team = Team.objects.get(id=self.team.id)
        self.assertEqual(team.name, self.team_data["name"])
        self.assertEqual(team.country, self.team_data["country"])

    def test_update_team(self):
        self.team.name = "Red Bull Racing"
        self.team.save()

        updated_team = Team.objects.get(id=self.team.id)
        self.assertEqual(updated_team.name, "Red Bull Racing")

    def test_delete_team(self):
        team_id = self.team.id
        self.team.delete()
        with self.assertRaises(Team.DoesNotExist):
            Team.objects.get(id=team_id)

    def tearDown(self):
        Team.objects.all().delete()
