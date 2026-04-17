# app/models/enums.py
import enum

class MediaType(enum.Enum):
    FILME = "filme"
    SERIE = "serie"
    ANIME = "anime"
    DORAMA = "dorama"
    LIVRO = "livro"
    REALITY = "reality"

class Classification(enum.Enum):
    POSITIVO = "valeu"
    NEUTRO = "neutro"
    NEGATIVO = "nao_valeu"

class Emotion(enum.Enum):
    FELIZ="feliz"; TRISTE="triste"; ANSIOSO="ansioso"
    MOTIVADO="motivado"; ENTEDIADO="entediado"; NEUTRO="neutro"