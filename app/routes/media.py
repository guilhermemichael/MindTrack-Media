# app/routes/media.py
from datetime import datetime, UTC

from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required

from app.extensions import db
from app.models.media import Media
from app.services.analytics import compute_delta_mood, compute_time_efficiency

bp = Blueprint("media", __name__)


@bp.post("/")
@login_required
def create_media():
    data = request.get_json()

    try:
        delta = compute_delta_mood(data["mood_before"], data["mood_after"])
        eff = compute_time_efficiency(data["rating"], data["duration_min"])

        media = Media(
            user_id=current_user.id,
            name=data["name"],
            media_type=data["media_type"],
            duration_min=data["duration_min"],
            rating=data["rating"],
            classification=data["classification"],
            mood_before=data["mood_before"],
            mood_after=data["mood_after"],
            primary_emotion=data["primary_emotion"],
            watched_at=datetime.now(UTC),
            delta_mood=delta,
            time_efficiency=eff,
        )

        db.session.add(media)
        db.session.commit()

        return jsonify({"message": "Midia adicionada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
