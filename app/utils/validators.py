# app/utils/validators.py
from datetime import datetime

class ValidationError(Exception): pass

def validate_media_payload(p):
    required = ["user_id","name","media_type","duration_min","rating",
                "classification","mood_before","mood_after","primary_emotion"]
    for k in required:
        if k not in p: raise ValidationError(f"{k} ausente")

    duration = int(p["duration_min"])
    rating = float(p["rating"])
    mb = int(p["mood_before"]); ma = int(p["mood_after"])

    if duration <= 0: raise ValidationError("duration_min <= 0")
    if not (0 <= rating <= 10): raise ValidationError("rating fora [0,10]")
    if not (0 <= mb <= 10 and 0 <= ma <= 10): raise ValidationError("mood fora [0,10]")

    return {
        **p,
        "duration_min": duration,
        "rating": rating,
        "mood_before": mb,
        "mood_after": ma,
        "watched_at": datetime.fromisoformat(p.get("watched_at")) if p.get("watched_at") else None
    }