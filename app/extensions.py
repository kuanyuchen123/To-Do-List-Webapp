from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = 'Login first!'
login_manager.login_view = 'login'
cache = Cache(app, config={'CACHE_TYPE': 'simple'})