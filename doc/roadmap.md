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

1 Requirement für LLM-Antwort ergänzen – erledigt (2026-09-25): C12, F12, B10, T5 und T1 in `requirements.md`.
  Antwort nur auf Knopfdruck („Antwort generieren") zu einer Suche mit Treffern; Kontext sind
  ausschließlich die Suchtreffer (inkl. Bühne/Tag/Zeiten); bei LLM-Ausfall bleiben die Treffer
  sichtbar; kein Chat. Offen: Zeitlimit (klärt Schritt 6)

2 LLM auswählen (manuell) – erledigt: Ollama, Modell `qwen3-instruct:4b` (in T1 aufgenommen)

3 Festlegen, welche Retrieval-Daten an das LLM gehen – erledigt (2026-09-25): genau die Suchtreffer
  (Name, Genre, Beschreibung, Bühne, Tag, Start/Ende) plus serverseitig berechneter Status
  „vorbei / läuft gerade / kommt noch", keine aktuelle Uhrzeit, keine IDs/Scores. Details:
  `doc/architecture.md` (Abschnitt „Generierte Antwort (LLM/RAG)"), B10 ergänzt

4 Kontextformat definieren – erledigt (2026-09-25): Retrieval-Treffer als Klartext unter
  „Gefundene Acts:", ein nummerierter Block pro Act (`1.` = Rang) mit den Zeilen Artist, Genre,
  Beschreibung, Bühne, Zeit (Tag + Uhrzeit), Status; Frage am Ende der User-Nachricht, Regeln in
  der System-Nachricht. Details und Beispiel: `doc/architecture.md` („Kontextformat")

5 System-Prompt / Regeln definieren – erledigt (2026-09-25): erster Entwurf auf Basis des
  Beispiel-Prompts (nur Kontext, nichts erfinden, sagen wenn Informationen nicht reichen, Status
  beachten, nur passende Acts, Acts beim Namen mit Tag/Zeit/Bühne, kurz auf Deutsch ohne
  Formatierung). Text und Begründung: `doc/architecture.md` („System-Prompt")

6 LLM mit festem Mock-Kontext separat ausprobieren – erledigt (2026-09-25): Wegwerf-Skript, 7
  Testfragen gegen `qwen3-instruct:4b`. Nichts erfunden, Fragen außerhalb des Kontexts sauber
  abgelehnt; Schwachstelle: vergangene und schwach passende Acts werden teils trotzdem genannt
  (auch bei `llama3.1:8b`). Folgen: System-Prompt nachgeschärft (v2), Wochentag im Kontext
  ausgeschrieben, Kontext nach Status sortiert (laufende/kommende vor vergangenen Acts – damit
  tauchten vergangene Acts nicht mehr in Empfehlungen auf), Temperatur 0.2, Zeitlimit 60 s
  (Antworten 2–35 s). Bekannte Einschränkung: schwach passende Acts werden teils mitgenannt.
  Details: `doc/architecture.md` („Ausprobieren mit Mock-Kontext")

7 Retrieval + LLM verbinden – Top-5-Treffer als Kontext an das LLM übergeben – erledigt (2026-09-25):
  `app/llm.py` (System-Prompt, `build_context()`, `build_messages()`), `schedule.act_phase()`,
  `crud.acts_for_artists()` liefert zusätzlich Genre/Beschreibung; 11 neue Tests (77 grün).
  End-to-End per Wegwerf-Skript gegen Neon + Ollama: Pipeline funktioniert; bei „Blasinstrumente"
  nennt das Modell einen vergangenen Act ohne Hinweis und erfindet eine Eigenschaft
  (→ Testfall für Schritt 11). Details: `doc/architecture.md` („Retrieval und LLM verbinden")

8 LLM-Service im Backend integrieren – Ollama, Modell, Prompt und Fehlerbehandlung kapseln – erledigt (2026-09-25):
  `app/llm.py` ruft Ollama per `urllib` (keine neue Dependency) auf; `generate_answer()` als
  Einstiegspunkt, alle Fehler (nicht erreichbar, Zeitlimit 60 s, HTTP-Fehler, kaputte/leere
  Antwort) als `LLMUnavailableError`. 13 neue Tests (90 grün), manuell gegen echtes Ollama
  geprüft (Antwort, nicht erreichbar, Modell fehlt). Details: `doc/architecture.md`
  („LLM-Service im Backend")

9 API erweitern – generierte Antwort zusätzlich zu den Suchtreffern zurückgeben – erledigt (2026-09-25):
  eigener Endpunkt `GET /api/answer?q=` (Antwort auf Knopfdruck, F12), `/api/search` unverändert.
  Gleiche Suche, dann `generate_answer()`; immer `200` mit `{status: ok|no_hits|unavailable,
  answer}`; ohne Treffer kein LLM-Aufruf. LLM als Dependency `llm_send()`. 6 neue Tests
  (96 grün); gegen echten Server geprüft (erster Aufruf 74 s wegen Modell-Laden, danach
  17–22 s). Details: `doc/architecture.md` („`GET /api/answer`")

10 Frontend anbinden – Dummy-Antwort durch echte LLM-Antwort ersetzen – erledigt (2026-09-25):
  (keine Dummy-Antwort vorhanden, direkt echt angebunden) Button „Antwort generieren" unter
  der Überschrift der Suchtreffer, nur bei Treffern; Ladehinweis, Antwort in abgesetztem Kasten
  über der Trefferliste, Hinweis „gerade nicht verfügbar" mit erneutem Versuch; neue Suche
  entfernt die Antwort, veraltete Antworten werden verworfen. `style.css` neu erzeugt.
  Erstmals im echten Browser geprüft (Headless Chrome per DevTools-Protokoll, 360 px, gegen
  echten Server + Ollama, Screenshots) – damit auch der offene Live-Browsertest aus Phase 1
  nachgeholt. Details: `doc/architecture.md` („Frontend", „Browsertest")

11 Fehlerfälle / Halluzinationsschutz – keine Treffer, Timeout, keine erfundenen Informationen

12 Tests – Kontextaufbau, LLM-Aufruf, API und Fehlerfälle testen; LLM-Aufruf mocken

13 Review + Dokumentation – vollständigen RAG-Ablauf und Architektur dokumentieren
