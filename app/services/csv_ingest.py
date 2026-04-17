# app/services/csv_ingest.py
import csv
from datetime import datetime
from app.services.analytics import compute_delta_mood, compute_time_efficiency

REQUIRED = {"name", "media_type", "duration_min", "rating", "mood_before", "mood_after", "classification", "primary_emotion", "watched_at"}

def _coerce_int(v, field):
    try:
        return int(v)
    except:
        raise ValueError(f"{field} inválido")

def _coerce_float(v, field):
    try:
        return float(v)
    except:
        raise ValueError(f"{field} inválido")

def _parse_date(v):
    # múltiplos formatos
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(v, fmt)
        except:
            pass
    raise ValueError("data inválida")

def clean_row(row: dict) -> dict:
    # mapping flexível
    name = row.get("name") or row.get("title")
    media_type = row.get("media_type")
    duration = _coerce_int(row.get("duration_min"), "duration_min")
    rating = _coerce_float(row.get("rating"), "rating")
    mb = _coerce_int(row.get("mood_before"), "mood_before")
    ma = _coerce_int(row.get("mood_after"), "mood_after")
    cls = row.get("classification")
    emo = row.get("primary_emotion")
    date = _parse_date(row.get("watched_at"))

    # validações duras
    if not (0 <= rating <= 10): raise ValueError("rating fora do intervalo")
    if duration <= 0: raise ValueError("duration inválida")
    if not (0 <= mb <= 10 and 0 <= ma <= 10): raise ValueError("mood inválido")

    return {
        "name": name.strip(),
        "media_type": media_type,
        "duration_min": duration,
        "rating": rating,
        "mood_before": mb,
        "mood_after": ma,
        "classification": cls,
        "primary_emotion": emo,
        "watched_at": date
    }

def ingest_csv(file_stream, user_id):
    reader = csv.DictReader(file_stream.read().decode("utf-8", errors="ignore").splitlines())
    ok, errors = 0, []

    for i, row in enumerate(reader, start=1):
        try:
            data = clean_row(row)
            delta = compute_delta_mood(data["mood_before"], data["mood_after"])
            eff = compute_time_efficiency(data["rating"], data["duration_min"])
            yield {
                **data,
                "user_id": user_id,
                "delta_mood": delta,
                "time_efficiency": eff
            }
            ok += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e), "raw": row})

    return ok, errors