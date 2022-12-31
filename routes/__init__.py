# This file is part of https://github.com/jainamoswal/Flask-Example.
# Usage covered in <IDC lICENSE>
# Jainam Oswal. <jainam.me>


# Import Libraries
import os
import importlib
from pathlib import Path


# Get all files.
views = ['admin.py', 'patient.py', 'therapist.py','auth.py']
# Import all files from modules folder.
# for view in views:
importlib.import_module('routes.admin')
importlib.import_module('routes.patient')
importlib.import_module('routes.therapist')
importlib.import_module('routes.auth')


