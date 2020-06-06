import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or "2457b5e094116c40b647f440ae62d539"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # TEMPLATES_AUTO_RELOAD = True
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get(
        "GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get(
        "GOOGLE_OAUTH_CLIENT_SECRET")
    LISTINGS_PER_PAGE = 6
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get(
        "EMAIL_USER")
    MAIL_PASSWORD = os.environ.get(
        "EMAIL_PASSWORD")
