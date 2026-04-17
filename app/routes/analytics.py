# app/routes/analytics.py
from flask import Blueprint, jsonify, session
from sqlalchemy import func
from app.extensions import db
from app.models.media import Media

bp = Blueprint("analytics", __name__)

@bp.get("/summary")
def get_summary():
    if "user_id" not in session:
        return jsonify({"error": "Não autorizado"}), 401

    user_id = session["user_id"]

    # Aggregate queries
    total_medias = db.session.query(func.count(Media.id)).filter_by(user_id=user_id).scalar()

    avg_delta_mood = db.session.query(func.avg(Media.delta_mood)).filter_by(user_id=user_id).scalar()
    avg_time_efficiency = db.session.query(func.avg(Media.time_efficiency)).filter_by(user_id=user_id).scalar()

    # Group by media_type
    type_stats = db.session.query(
        Media.media_type,
        func.avg(Media.delta_mood).label("avg_delta"),
        func.avg(Media.time_efficiency).label("avg_eff"),
        func.count(Media.id).label("count")
    ).filter_by(user_id=user_id).group_by(Media.media_type).all()

    type_data = {}
    for row in type_stats:
        type_data[row.media_type.value] = {
            "avg_delta_mood": float(row.avg_delta) if row.avg_delta else 0,
            "avg_time_efficiency": float(row.avg_eff) if row.avg_eff else 0,
            "count": row.count
        }

    # Top 10 by time_efficiency
    top_eff = db.session.query(Media).filter_by(user_id=user_id).order_by(Media.time_efficiency.desc()).limit(10).all()
    top_list = [{"id": m.id, "name": m.name, "time_efficiency": float(m.time_efficiency)} for m in top_eff]

    # Time series: daily avg delta_mood (last 30 days or something, but for simplicity, all)
    # For MVP, just return overall

    return jsonify({
        "total_medias": total_medias,
        "avg_delta_mood": float(avg_delta_mood) if avg_delta_mood else 0,
        "avg_time_efficiency": float(avg_time_efficiency) if avg_time_efficiency else 0,
        "by_type": type_data,
        "top_efficiency": top_list
    })