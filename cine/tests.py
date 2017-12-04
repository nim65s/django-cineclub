from django.test import TestCase

from .models import Film


class TestFilm(TestCase):
    def test_film(self):
        Film.objects.create(**Film.get_imdb_dict('tt0096283'))
        self.assertEqual(Film.objects.count(), 1)
