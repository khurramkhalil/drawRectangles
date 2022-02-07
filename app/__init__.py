from flask import Flask
from config import Config
from flask_caching import Cache

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DOWNLOAD_FOLDER = 'downloads/'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

cache = Cache(app)
with app.app_context():
    cache.clear()

from app import routes
