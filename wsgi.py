# ============================================================
# PythonAnywhere WSGI file
# Place this content into /var/www/pjlive12_pythonanywhere_com_wsgi.py
# ============================================================
import sys
import os

path = '/home/pjlive12/library_management_system'
if path not in sys.path:
    sys.path.insert(0, path)

os.chdir(path)

from database import init_db
init_db()

from app import app as application
