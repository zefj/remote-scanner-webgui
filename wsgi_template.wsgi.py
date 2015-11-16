#!/usr/bin/python
import sys
import logging
import os

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/scannerapp/")
os.chdir("/var/www/scannerapp/")

from scannerapp import app as application
application.secret_key = 'YOUR-SECRET-KEY'
