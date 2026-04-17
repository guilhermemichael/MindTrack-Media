# app/routes/upload.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.media import Media
from app.services.csv_ingest import ingest_csv

bp = Blueprint("upload", __name__)

@bp.post("/csv")
@login_required
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        medias = list(ingest_csv(file, current_user.id))
        # Batch insert
        db.session.bulk_insert_mappings(Media, medias)
        db.session.commit()
        return jsonify({"message": f"Inserted {len(medias)} medias"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400