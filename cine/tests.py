from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Cinephile, Film

FILM = 'tt0096283'


class TestFilm(TestCase):
    def setUp(self):
        for name in ('a', 'b', 'i', 's'):
            create = User.objects.create_superuser if name == 's' else User.objects.create_user
            user = create(username=name, email=f'{name}@example.com', password=name)
            Cinephile.objects.create(user=user, actif=name != 'i')

    def test_film(self):
        r = self.client.get(reverse('cine:films'))
        self.assertEqual(r.status_code, 200)

        r = self.client.get(reverse('cine:ajout_film'))
        self.assertEqual(r.status_code, 302)

        self.client.login(username='i', password='i')
        r = self.client.get(reverse('cine:ajout_film'))
        self.assertEqual(r.status_code, 302)

        self.client.login(username='a', password='a')
        r = self.client.get(reverse('cine:ajout_film'))
        self.assertEqual(r.status_code, 200)

        r = self.client.get(reverse('cine:ajout_film'), {'imdb_id': FILM})
        self.assertEqual(r.status_code, 200)
        self.assertIn('My Neighbor Totoro', r.content.decode())

        self.assertEqual(Film.objects.count(), 0)
        form = Film.get_imdb_dict(FILM)
        self.client.post(reverse('cine:ajout_film'), form)
        self.assertEqual(Film.objects.count(), 1)
        film = Film.objects.first()
        self.assertEqual(str(film), 'My Neighbor Totoro')

        form['name'] = 'となりのトトロ'
        r = self.client.post(reverse('cine:maj_film', kwargs={'slug': film.slug}), form)
        film = Film.objects.first()
        self.assertEqual(str(film), 'となりのトトロ')

        self.client.login(username='b', password='b')
        form['name'] = 'rototo'
        r = self.client.post(reverse('cine:maj_film', kwargs={'slug': film.slug}), form)
        film = Film.objects.first()
        self.assertEqual(str(film), 'となりのトトロ')
