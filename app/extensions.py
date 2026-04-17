# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy(session_options={"autoflush": False})
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
