# Project Roadmap 

## Phase 1 - Vectorsuche


1  Frontend-Zielbild – erledigt (2026-09-22): Suchbereich mit Mock-Ergebnissen in `static/`

2  Requirement – erledigt (2026-09-23): C11, F11, B8, T4 in `requirements.md`

3  Suchinhalt festlegen – erledigt (2026-09-23): Artist (name, genre, description), siehe B8/B9

4  Domain Model dokumentieren – erledigt (2026-09-23): Artist + genre, description, embedding

5  Embedding-Modell ausprobieren (Manuell) – erledigt: paraphrase-multilingual-MiniLM-L12-v2, 384 Dimensionen

6  pgvector aktivieren (Manuell) – erledigt: Erweiterung `vector` in Neon aktiv

7  embedding-Spalte technisch anlegen – erledigt (2026-09-23): genre, description, embedding vector(384) auf Artist

8  Embeddings erzeugen + speichern – erledigt (2026-09-23): `python -m app.embeddings`, 44 Artists

9  Vektorsuche direkt testen

10 Backend / SQLAlchemy-Suche

11 Search-API

12 Frontend anbinden

13 Tests + Review