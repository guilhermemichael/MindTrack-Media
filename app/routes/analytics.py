from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models.enums import Emotion, MediaType
from app.models.media import Media
from app.services.analytics import build_consumption_insight

bp = Blueprint("analytics", __name__)

MEDIA_TYPE_LABELS = {
    MediaType.FILME: "Filme",
    MediaType.SERIE: "Serie",
    MediaType.ANIME: "Anime",
    MediaType.DORAMA: "Dorama",
    MediaType.LIVRO: "Livro",
    MediaType.REALITY: "Reality",
}

EMOTION_LABELS = {
    Emotion.FELIZ: "Feliz",
    Emotion.TRISTE: "Triste",
    Emotion.ANSIOSO: "Ansioso",
    Emotion.MOTIVADO: "Motivado",
    Emotion.ENTEDIADO: "Entediado",
    Emotion.NEUTRO: "Neutro",
}


@bp.get("/summary")
@login_required
def get_summary():
    user_id = current_user.id

    total_medias = db.session.query(func.count(Media.id)).filter_by(user_id=user_id).scalar()
    total_duration_min = db.session.query(func.coalesce(func.sum(Media.duration_min), 0)).filter_by(user_id=user_id).scalar()
    avg_rating = db.session.query(func.avg(Media.rating)).filter_by(user_id=user_id).scalar()
    avg_delta_mood = db.session.query(func.avg(Media.delta_mood)).filter_by(user_id=user_id).scalar()
    avg_time_efficiency = db.session.query(func.avg(Media.time_efficiency)).filter_by(user_id=user_id).scalar()

    type_stats = (
        db.session.query(
            Media.media_type,
            func.avg(Media.delta_mood).label("avg_delta"),
            func.avg(Media.time_efficiency).label("avg_eff"),
            func.avg(Media.rating).label("avg_rating"),
            func.count(Media.id).label("count"),
        )
        .filter_by(user_id=user_id)
        .group_by(Media.media_type)
        .all()
    )

    type_data = {}
    for row in type_stats:
        type_data[row.media_type.value] = {
            "label": MEDIA_TYPE_LABELS.get(row.media_type, row.media_type.value.title()),
            "avg_delta_mood": float(row.avg_delta) if row.avg_delta else 0,
            "avg_time_efficiency": float(row.avg_eff) if row.avg_eff else 0,
            "avg_rating": float(row.avg_rating) if row.avg_rating else 0,
            "count": row.count,
        }

    top_eff = (
        db.session.query(Media)
        .filter_by(user_id=user_id)
        .order_by(Media.time_efficiency.desc())
        .limit(10)
        .all()
    )
    top_list = [
        {
            "id": m.id,
            "name": m.name,
            "time_efficiency": float(m.time_efficiency),
            "media_type": m.media_type.value,
            "media_type_label": MEDIA_TYPE_LABELS.get(m.media_type, m.media_type.value.title()),
        }
        for m in top_eff
    ]

    timeline_rows = (
        db.session.query(Media)
        .filter_by(user_id=user_id)
        .order_by(Media.watched_at.asc())
        .limit(14)
        .all()
    )
    mood_timeline = [
        {
            "label": media.watched_at.strftime("%d/%m"),
            "delta_mood": media.delta_mood,
            "rating": float(media.rating),
        }
        for media in timeline_rows
    ]

    recent_rows = (
        db.session.query(Media)
        .filter_by(user_id=user_id)
        .order_by(Media.watched_at.desc())
        .limit(5)
        .all()
    )
    recent_entries = [
        {
            "id": media.id,
            "name": media.name,
            "rating": float(media.rating),
            "delta_mood": media.delta_mood,
            "media_type": media.media_type.value,
            "media_type_label": MEDIA_TYPE_LABELS.get(media.media_type, media.media_type.value.title()),
            "watched_at_label": media.watched_at.strftime("%d/%m %H:%M"),
        }
        for media in recent_rows
    ]

    dominant_type_row = max(type_stats, key=lambda row: row.count, default=None)
    dominant_type_label = (
        MEDIA_TYPE_LABELS.get(dominant_type_row.media_type, dominant_type_row.media_type.value.title())
        if dominant_type_row
        else None
    )

    top_emotion_row = (
        db.session.query(Media.primary_emotion, func.count(Media.id).label("count"))
        .filter_by(user_id=user_id)
        .group_by(Media.primary_emotion)
        .order_by(func.count(Media.id).desc())
        .first()
    )
    top_emotion_label = (
        EMOTION_LABELS.get(top_emotion_row.primary_emotion, top_emotion_row.primary_emotion.value.title())
        if top_emotion_row
        else None
    )

    insight = build_consumption_insight(
        total_medias=int(total_medias or 0),
        avg_delta_mood=float(avg_delta_mood or 0),
        avg_time_efficiency=float(avg_time_efficiency or 0),
        top_emotion_label=top_emotion_label,
        dominant_type_label=dominant_type_label,
    )

    return jsonify(
        {
            "total_medias": int(total_medias or 0),
            "total_duration_min": int(total_duration_min or 0),
            "avg_rating": float(avg_rating) if avg_rating else 0,
            "avg_delta_mood": float(avg_delta_mood) if avg_delta_mood else 0,
            "avg_time_efficiency": float(avg_time_efficiency) if avg_time_efficiency else 0,
            "by_type": type_data,
            "top_efficiency": top_list,
            "mood_timeline": mood_timeline,
            "recent_entries": recent_entries,
            "dominant_type_label": dominant_type_label,
            "top_emotion_label": top_emotion_label,
            "insight": insight,
        }
    )
