from django.contrib.admin import site

from .models import Cinephile, Film, Soiree

for model in [Cinephile, Film, Soiree]:
    site.register(model)
