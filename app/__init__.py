from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
import time
import os
import logging

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
moment = Moment(app)

login_manager.session_protection = 'strong'
login_manager.login_view = 'app.login'
login_manager.init_app(app)

handler = logging.FileHandler('flask.log', encoding='UTF-8')
handler.setLevel(logging.DEBUG)
logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)


from app import views, models
from .models import Permission
@app.context_processor
def inject_permissions():
    return dict(Permission=Permission)
