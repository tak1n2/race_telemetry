import unittest
from apps.core.models.track import Track


class TrackModelTests(unittest.TestCase):

    def setUp(self):
        self.track_data = {
            "name": "Monza",
            "location": "Italy",
            "length_km": 5.793,
            "turns": 11,
        }
        self.track = Track.objects.create(**self.track_data)

    def test_create_track(self):
        track = Track.objects.get(id=self.track.id)
        self.assertEqual(track.name, self.track_data["name"])
        self.assertEqual(track.location, self.track_data["location"])
        self.assertEqual(track.length_km, self.track_data["length_km"])
        self.assertEqual(track.turns, self.track_data["turns"])

    def test_update_track(self):
        self.track.name = "Silverstone"
        self.track.location = "UK"
        self.track.turns = 18
        self.track.save()

        updated_track = Track.objects.get(id=self.track.id)
        self.assertEqual(updated_track.name, "Silverstone")
        self.assertEqual(updated_track.location, "UK")
        self.assertEqual(updated_track.turns, 18)

    def test_delete_track(self):
        track_id = self.track.id
        self.track.delete()
        with self.assertRaises(Track.DoesNotExist):
            Track.objects.get(id=track_id)

    def tearDown(self):
        Track.objects.all().delete()
