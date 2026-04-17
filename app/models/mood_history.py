# app/models/mood_history.py
from app.extensions import db
from sqlalchemy import ForeignKey, func, Index, CheckConstraint

class MoodHistory(db.Model):
    __tablename__ = "mood_history"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    media_id = db.Column(db.BigInteger, ForeignKey("medias.id", ondelete="CASCADE"), nullable=True, index=True)

    mood = db.Column(db.SmallInteger, nullable=False)  # 0–10
    recorded_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        CheckConstraint("mood >= 0 AND mood <= 10", name="ck_mood_bounds"),
        Index("ix_mood_user_time", "user_id", "recorded_at"),
    )