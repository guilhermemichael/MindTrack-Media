# app/models/media.py
from app.extensions import db
from sqlalchemy import CheckConstraint, Index, func, ForeignKey
from app.models.enums import MediaType, Classification, Emotion

class Media(db.Model):
    __tablename__ = "medias"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name = db.Column(db.String(200), nullable=False)
    media_type = db.Column(db.Enum(MediaType), nullable=False, index=True)

    duration_min = db.Column(db.Integer, nullable=False)  # minutos
    rating = db.Column(db.Numeric(3,1), nullable=False)   # 0.0–10.0

    classification = db.Column(db.Enum(Classification), nullable=False, index=True)

    mood_before = db.Column(db.SmallInteger, nullable=False)  # 0–10
    mood_after = db.Column(db.SmallInteger, nullable=False)   # 0–10
    primary_emotion = db.Column(db.Enum(Emotion), nullable=False, index=True)

    watched_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)

    # métricas materializadas (cache para performance)
    delta_mood = db.Column(db.SmallInteger, nullable=False)
    time_efficiency = db.Column(db.Numeric(6,3), nullable=False)  # rating / (duration_min/60)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("duration_min > 0 AND duration_min <= 10000", name="ck_duration_bounds"),
        CheckConstraint("rating >= 0 AND rating <= 10", name="ck_rating_bounds"),
        CheckConstraint("mood_before >= 0 AND mood_before <= 10", name="ck_mood_before_bounds"),
        CheckConstraint("mood_after >= 0 AND mood_after <= 10", name="ck_mood_after_bounds"),
        Index("ix_media_user_date", "user_id", "watched_at"),
        Index("ix_media_user_type", "user_id", "media_type"),
    )