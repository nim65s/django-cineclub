from django.test import TestCase
from django.urls import reverse

from .models import Film


class TestFilm(TestCase):
    def test_film(self):
        Film.objects.create(**Film.get_imdb_dict('tt0096283'))
        self.assertEqual(Film.objects.count(), 1)
        film = Film.objects.first()
        self.assertEqual(str(film), 'My Neighbor Totoro')

        r = self.client.get(reverse('cine:films'))
        self.assertEqual(r.status_code, 200)
