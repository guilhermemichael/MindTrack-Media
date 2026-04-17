from decimal import Decimal, ROUND_HALF_UP


def compute_delta_mood(mood_before: int, mood_after: int) -> int:
    return int(mood_after) - int(mood_before)


def compute_time_efficiency(rating: float, duration_min: int) -> Decimal:
    # Avoid division by zero. The model constraint already blocks invalid values.
    val = (Decimal(60) * Decimal(str(rating))) / Decimal(duration_min)
    return val.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def build_consumption_insight(
    total_medias: int,
    avg_delta_mood: float,
    avg_time_efficiency: float,
    top_emotion_label: str | None,
    dominant_type_label: str | None,
) -> str:
    if not total_medias:
        return "Seu painel ainda esta em branco. Registre a primeira midia para revelar padroes emocionais e de eficiencia."

    if avg_delta_mood < 0:
        return (
            f"Seu consumo recente esta puxando seu humor para baixo. "
            f"Revise especialmente os titulos de {dominant_type_label or 'midia'} e priorize experiencias com efeito mais leve."
        )

    if avg_delta_mood >= 2 and avg_time_efficiency >= 4:
        return (
            f"Voce encontrou uma zona forte de consumo: impacto emocional positivo e boa eficiencia. "
            f"{top_emotion_label or 'Sua emocao dominante'} aparece com frequencia como resposta final."
        )

    if avg_time_efficiency < 2:
        return (
            "Voce esta investindo bastante tempo para pouco retorno percebido. "
            "Vale comparar duracao, nota e emocao final para filtrar melhor suas escolhas."
        )

    return (
        f"Seu padrao atual parece estavel. {dominant_type_label or 'Esse tipo de conteudo'} domina seus registros, "
        "entao pequenas mudancas de selecao ja podem melhorar bastante o resultado geral."
    )
