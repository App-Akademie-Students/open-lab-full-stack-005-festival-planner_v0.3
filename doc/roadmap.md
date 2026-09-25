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

9  Vektorsuche direkt testen – erledigt (2026-09-24): Wegwerf-Skript, `Artist.embedding.cosine_distance(query_vector)` per SQLAlchemy gegen Neon, 4 deutsche Testanfragen. Treffer überwiegend passend (z. B. "Musik mit Blasinstrumenten" → Morning Brass, Brass Explosion vorn), auch umgangssprachlich (T4). Bei einer Anfrage lag ein thematisch abweichender Act knapp vor den passenderen (Distanzen sehr nah beieinander) – kein Fehler, aber ein Punkt für den späteren Review der Trefferqualität.

10 Backend / SQLAlchemy-Suche – erledigt (2026-09-24): drei Funktionen in `app/crud.py` –
   `search_top_artists()` (pgvector `cosine_distance()`, Top 5 Artists, kein Schwellenwert),
   `acts_for_artists()` (Join zu den Acts, sortiert nach Artist-Rang dann Zeit, unabhängig von
   Tages-/Bühnenfilter, inkl. vergangener Acts) und `search_acts()` als Kombination. Nur
   `acts_for_artists()` ist automatisiert getestet (`tests/test_crud.py`, 5 Tests); der
   pgvector-Teil ist manuell gegen Neon verifiziert, Ergebnis deckt sich mit Schritt 9. Details:
   `doc/architecture.md` (Abschnitt „Semantische Suche").

11 Search-API – erledigt (2026-09-24): `GET /api/search?q=` in `app/routers.py`. `q` Pflicht,
   nach Trimmen nicht leer (sonst `422`). Embeddet `q` (`app/embeddings.py::embed_texts()`) und
   ruft `crud.search_top_artists()` + `crud.acts_for_artists()` auf, über die austauschbare
   Dependency `search_artist_ids()` (wie `festival_now`) getrennt, damit Tests weder Modell noch
   pgvector brauchen. Antwort: `{ items: [{id, title, stage, day, starts_at, ends_at}] }` – `day`
   zusätzlich zu `/api/program`, wie von F11 verlangt. 5 neue Tests
   (`tests/test_search_api.py`); End-to-End gegen Neon mit echtem Modell manuell verifiziert
   (200 mit sinnvollen Treffern, 422 bei leerer/fehlender Anfrage). Details:
   `doc/architecture.md` (Abschnitt „HTTP-API" und „Semantische Suche").

12 Frontend anbinden – erledigt (2026-09-24): `static/app.js` ruft bei Suche (Formular-Submit
   oder Beispiel-Button) `GET /api/search?q=` auf statt der festen Mock-Daten aus Schritt 1;
   `MOCK_SEARCH_RESULTS` entfernt. Ergebnisliste zeigt Rang, Titel, Tag/Zeit/Bühne (kein
   Ähnlichkeits-Score mehr, die API liefert keinen). Zustände in `index.html`/`app.js`: leere
   Anfrage („Bitte gib eine Suchanfrage ein.", F11), Ladehinweis „Suche läuft…" (erster Aufruf
   lädt das Modell und kann mehrere Sekunden dauern), keine Treffer („Keine passenden Acts
   gefunden.", F11), veraltete Antworten werden verworfen (`latestSearchRequest`, wie beim
   Programmfilter T-23). Verifiziert gegen den echten, laufenden Server (uvicorn, Neon, echtes
   Modell) per HTTP: `/`, `/app.js` und `/api/search` liefern die neue, verdrahtete Fassung,
   `q` leer/fehlend weiterhin `422`, eine echte Anfrage liefert die erwarteten Treffer. Kein
   Browser-Automatisierungstool auf diesem Rechner verfügbar – keine Screenshot-Verifikation,
   nur die HTTP-Ebene geprüft.

13 Tests + Review – erledigt (2026-09-24): Review als Nachtrag in `doc/review.md` (Abschnitt
   10), Backlog-Story `US-11` in `doc/backlog.md` ergänzt (rückwirkend für die Schritte 1–12).
   Urteil: „Freigeben mit nicht blockierenden Änderungswünschen", keine Blocker; offen ist
   T-29 (veraltete Regel in `static/style.css`, kosmetisch). 66 Tests grün. Damit ist
   Vektorsuche Phase 1 abgeschlossen.

## Phase 2 – LLM Integration

1 Requirement für LLM-Antwort ergänzen

2 LLM auswählen (manuell) - verwende OLLAMA - qwen3-instruct:4b

3 Festlegen, welche Retrieval-Daten an das LLM gehen

4 Kontextformat definieren

5 System-Prompt / Regeln definieren

6 LLM mit festem Mock-Kontext separat ausprobieren

7 Retrieval + LLM verbinden – Top-5-Treffer als Kontext an das LLM übergeben

8 LLM-Service im Backend integrieren – Ollama, Modell, Prompt und Fehlerbehandlung kapseln

9 API erweitern – generierte Antwort zusätzlich zu den Suchtreffern zurückgeben

10 Frontend anbinden – Dummy-Antwort durch echte LLM-Antwort ersetzen

11 Fehlerfälle / Halluzinationsschutz – keine Treffer, Timeout, keine erfundenen Informationen

12 Tests – Kontextaufbau, LLM-Aufruf, API und Fehlerfälle testen; LLM-Aufruf mocken

13 Review + Dokumentation – vollständigen RAG-Ablauf und Architektur dokumentieren
