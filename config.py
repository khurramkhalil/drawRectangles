import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET.KEY') or 'you-will-never-guess'
    MAX_CONTENT_LENGTH = 10024 * 10024
    UPLOAD_EXTENSIONS = ['xls', 'xlsx', 'csv']

    # configurations for flask-caching
    DEBUG = True  # some Flask specific configs
    CACHE_TYPE = 'simple'  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 0