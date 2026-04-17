# MindTrack Media

Sistema de analise comportamental baseado no consumo de midia.

## O que ele faz
- Analisa impacto emocional de filmes, series, animes, doramas, livros e reality shows.
- Calcula delta de humor e eficiencia de tempo a partir do consumo registrado.
- Detecta padroes de comportamento com dashboard, ranking e insight automatico.

## Diferencial
O produto nao mostra apenas o que voce gosta. Ele mostra o que te afeta, quanto valor gera e como isso se repete no seu comportamento.

## Stack
- Python
- Flask
- Flask-Login
- SQLAlchemy
- SQLite
- Chart.js
- HTML, CSS e JavaScript

## Funcionalidades
- Cadastro e login com autenticacao persistente
- Registro de midia com contexto emocional
- Dashboard com KPIs e grafico de impacto emocional
- Distribuicao por tipo de conteudo
- Ranking de conteudos mais eficientes
- Insight automatico sobre padrao recente

## Como rodar
```bash
pip install -r requirements.txt
python run.py
```

## Banco e migrations
Se estiver com banco antigo ou schema defasado:

```bash
flask db upgrade
```

## Visao de produto
MindTrack Media transforma consumo subjetivo em dados quantificaveis, metricas analiticas e padroes interpretaveis para apoiar escolhas melhores de entretenimento.
