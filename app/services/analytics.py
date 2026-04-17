# app/services/analytics.py
from decimal import Decimal, ROUND_HALF_UP

def compute_delta_mood(mood_before: int, mood_after: int) -> int:
    return int(mood_after) - int(mood_before)

def compute_time_efficiency(rating: float, duration_min: int) -> Decimal:
    # evita divisão por zero (já protegido por constraint)
    val = (Decimal(60) * Decimal(str(rating))) / Decimal(duration_min)
    return val.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)