import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOADS_DIR_NAME = 'uploads'
UPLOADS_DIR = os.path.join(BASE_DIR, 'static/' + UPLOADS_DIR_NAME)
DB_PATH = os.path.join(BASE_DIR, 'debts.db')

if not os.path.exists(UPLOADS_DIR):
    os.mkdir(UPLOADS_DIR)