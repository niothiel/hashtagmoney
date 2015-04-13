import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
DB_PATH = os.path.join(BASE_DIR, 'debts.db')

if not os.path.exists(UPLOADS_DIR):
    os.mkdir(UPLOADS_DIR)