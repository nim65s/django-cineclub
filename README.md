CinéNim
=======

But
---
Ceci est une application de gestion d’un cinéclub. Plus ou moins.

Principe
--------
Les gens inscrits proposent des films et trient tous ceux proposés par ordre de préférence.

Ils renseignent également leurs disponibilités, et boum paf, la présente application indique quel film on regarde à quelle date.

Requirements
------------

* Django
* django-bootstrap3 (only if you use the provided templates)
* pytz
* Pillow

Quick start with the example project
------------

1. Clone this repo in your working directory

    ```bash
    git clone git@github.com:nim65s/django-cineclub.git
    cd django-cineclub
    ```

2. Create a virtualenv
    * Using virtualfish: `vf new mycineclub`
    * Using virtualenvwrapper: `mkvirtualenv mycineclub`
    * Using virtualenv: `virtualenv venv_mycineclub; source venv_mycineclub/bin/activate`
3. Install the package:
    * Directly from the repo: `pip install -e git://github.com/Nim65s/django-cineclub.git#egg=cine`
    * Built it yoursefl: `python setup.py sdist; pip install -U dist/*.tar.gz`
4. Go to the example dir: `cd mycineclub_example`
6. Update and populate your database, and launch the server

    ```python
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py runserver
    ```

7. Add some cinephile on [your browser](http://localhost:8000/admin/cine/cinephile/add/)
