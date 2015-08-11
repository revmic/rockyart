import os
import configparser

basedir = os.path.abspath(os.path.dirname(__file__))
configp = configparser.RawConfigParser()
configp.read(os.path.expanduser('~/.rockyart.cfg'))

INSTAGRAM_KEY = configp['instagram']['client_id']


class Config:
    SECRET_KEY = configp['site']['secretkey'] or 'hard to guess stuff'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SUBJECT_PREFIX = '[RockyArt]'
    MAIL_SENDER = 'RockyArt Admin <admin@rockypardoart.com>'
    # This is an email that will automatically become admin
    # ROCKY_ADMIN = os.environ.get('ROCKY_ADMIN')
    ROCKY_ADMIN = 'mhilema@gmail.com'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = configp['mail']['username']
    MAIL_PASSWORD = configp['mail']['password']

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
