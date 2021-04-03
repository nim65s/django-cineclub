# CinéNim
[![Build Status](https://travis-ci.org/nim65s/django-cineclub.svg?branch=master)](https://travis-ci.org/nim65s/django-cineclub)
[![Coverage Status](https://coveralls.io/repos/github/nim65s/django-cineclub/badge.svg?branch=master)](https://coveralls.io/github/nim65s/django-cineclub?branch=master)

## But
Ceci est une application de gestion d’un cinéclub. Plus ou moins.

## Principe
Les gens inscrits proposent des films et trient tous ceux proposés par ordre de préférence.

Ils renseignent également leurs disponibilités, et boum paf, la présente application indique quel film on regarde à quelle date.

## Requirements

* [Django](https://www.djangoproject.com/)
* [django-bootstrap4](https://github.com/zostera/django-bootstrap4) (only if you use the provided templates)
* [django-sortedm2m](https://github.com/jazzband/django-sortedm2m)
* [ndh](https://github.com/nim65s/ndh)
* pytz
* Pillow

## Quick start with the example project

1. Clone this repo in your working directory

    ```bash
    git clone git@github.com:nim65s/django-cineclub.git
    cd django-cineclub
    ```

2. Install requirements

    ```bash
    poetry install
    ```

3. Update and populate your database, and launch the server

    ```bash
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py runserver
    ```

4. Add some cinephile on [your browser](http://localhost:8000/admin/cine/cinephile/add/)
