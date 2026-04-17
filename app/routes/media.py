# app/routes/media.py
from flask import Blueprint, request, jsonify, session
from app.extensions import db
from app.models.media import Media
from app.services.analytics import compute_delta_mood, compute_time_efficiency
from app.utils.validators import validate_media_payload
from datetime import datetime

bp = Blueprint("media", __name__)

@bp.post("/")
def create_media():

    if "user_id" not in session:
        return jsonify({"error": "Não autorizado"}), 401

    data = request.get_json()

    try:
        delta = compute_delta_mood(data["mood_before"], data["mood_after"])
        eff = compute_time_efficiency(data["rating"], data["duration_min"])

        media = Media(
            user_id=session["user_id"],
            name=data["name"],
            media_type=data["media_type"],
            duration_min=data["duration_min"],
            rating=data["rating"],
            classification=data["classification"],
            mood_before=data["mood_before"],
            mood_after=data["mood_after"],
            primary_emotion=data["primary_emotion"],
            watched_at=datetime.utcnow(),
            delta_mood=delta,
            time_efficiency=eff
        )

        db.session.add(media)
        db.session.commit()

        return jsonify({"message": "Mídia adicionada"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400