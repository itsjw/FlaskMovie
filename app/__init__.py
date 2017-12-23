# encoding: utf-8
import os

from flask import Flask
from werkzeug.routing import BaseConverter
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_redis import FlaskRedis

from .utils import create_upload_dir


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:mysql@127.0.0.1:3306/flask_movie"
    REDIS_URL = "redis://127.0.0.1:6379/0"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = "密钥字符串"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_DIR = create_upload_dir(BASE_DIR)
    DEBUG = True


db = SQLAlchemy()
redis = FlaskRedis()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.url_map.converters["re"] = RegexConverter
    app.app_context().push()

    CSRFProtect(app)
    db.init_app(app)
    redis.init_app(app)

    from .admin import admin as admin_blueprint
    from .home import home as home_blueprint

    app.register_blueprint(admin_blueprint, url_prefix="/admin")
    app.register_blueprint(home_blueprint)

    return app
