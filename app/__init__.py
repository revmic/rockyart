from flask import Flask
from flask_admin import Admin
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
admin = Admin(name='rockyart manager', template_mode='bootstrap3')
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    admin.init_app(app)
    login_manager.init_app(app)
    # Explicitly creating db session using engine with options
    # to fix PythonAnywhere 5 minute timeout issue using pool_recycle
    # db.init_app(app)
    engine = db.create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'], pool_recycle=240)
    db.session = db.scoped_session(
        db.sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    # attach routes and custom error pages here
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
