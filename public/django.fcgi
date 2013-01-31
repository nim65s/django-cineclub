#!/usr/bin/python
import os
import sys
from os.path import dirname, abspath

_PROJECT_DIR = dirname(dirname(abspath(__file__)))
sys.path.insert(0, _PROJECT_DIR)
sys.path.insert(0, dirname(_PROJECT_DIR))

_PROJECT_NAME = _PROJECT_DIR.split('/')[-1]
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
