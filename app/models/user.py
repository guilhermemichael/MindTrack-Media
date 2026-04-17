# app/models/user.py
from app.extensions import db
from sqlalchemy import CheckConstraint, Index, func

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    medias = db.relationship("Media", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("length(username) >= 3", name="ck_username_len"),
    )