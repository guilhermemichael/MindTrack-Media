# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

db = SQLAlchemy(session_options={"autoflush": False})
migrate = Migrate()
bcrypt = Bcrypt()