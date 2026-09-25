# Projektstatus – Festival Planner

Stand: 2026-09-25. Kompakter Überblick über den aktuellen Stand, gedacht für externe
Gesprächspartner (z. B. ChatGPT), die das Projekt ohne Code und ohne alle Dokumente verstehen
sollen. Details stehen in den verlinkten Dokumenten unter `doc/`.

## 1. Projekt und Version

- **Name:** Festival Planner
- **Version/Phase:** v0.1 und v0.2 umgesetzt und reviewt. **v0.3 in Arbeit** – die
  Anforderungen liegen als Entwurf vor, fünf neue Stories sind umgesetzt (US-7 bis US-11).
- **Neue Entwicklungsphase:** semantische Vektorsuche **(Phase 1 abgeschlossen und reviewt,
  US-11)**, danach LLM/RAG (**Phase 2 begonnen**: Anforderungen und Modellwahl stehen) – siehe
  Abschnitt 6.
- Lernprojekt: schrittweise Entwicklung mit Claude, Dokumentation auf Deutsch, Code auf
  Englisch.

## 2. Projektziel

Ein minimalistischer Web-Planer für Festivalbesucher, der eine Frage beantwortet:
**„Wo läuft was zu welcher Zeit?"**

- Besucher sehen das Programm ohne Login, erkennen „läuft jetzt" / „kommt als Nächstes" und
  filtern nach Tag und Bühne – auf Smartphone und Desktop.
- Architektur-Leitlinie seit v0.2: nicht mehr „so klein wie möglich", sondern gut
  strukturiert und erweiterbar. Neue Struktur (Dateien, Schichten) kommt erst bei konkretem
  Bedarf, nicht auf Vorrat.
- Erweiterung in Planung: Acts semantisch suchen (nach Bedeutung statt exakter Begriffe),
  später Fragen in natürlicher Sprache per LLM beantworten – nur auf Basis der gefundenen
  Festivaldaten.

## 3. Architektur und Technologien

**Stack:** Python 3, FastAPI (uvicorn), SQLAlchemy, PostgreSQL bei Neon (Treiber `psycopg` v3,
Verbindung über `DATABASE_URL` in `.env` via `python-dotenv`), HTML + Vanilla JS (kein
JS-Framework, kein JS-Build), Tailwind CSS v4 (Standalone-CLI, erzeugtes CSS ist eingecheckt).
Tests: pytest + httpx (nur Dev), laufen gegen In-Memory-SQLite, nicht gegen Neon.
Für die Vektorsuche: PostgreSQL-Erweiterung pgvector (in Neon aktiviert, Python-Paket
`pgvector`) und das Embedding-Modell `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
(384 Dimensionen, mehrsprachig), lokal über `sentence-transformers` (PyTorch).

Ein Prozess (uvicorn) liefert API und Frontend aus. Flache Modulstruktur:

| Datei | Aufgabe |
|---|---|
| `app/main.py` | App-Objekt, Lifespan (`init_db()`), bindet Router und `static/` ein |
| `app/routers.py` | API-Endpunkte und Pydantic-Antwortmodelle |
| `app/crud.py` | Datenbank-Queries (Joins über `Artist`/`Stage`) |
| `app/schedule.py` | Reine Business-Logik: Festival-Zeit, Festivaltag, Status „now"/„next" |
| `app/models.py` | ORM-Modelle `Artist`, `Stage`, `Act`; `EMBEDDING_DIM = 384` |
| `app/db.py` | Engine, Session, `init_db()`; bricht ohne `DATABASE_URL` mit klarer Meldung ab |
| `app/seed.py` | Seed-Skript: vier Festivaltage ab heute, 3 Bühnen, Genre und Beschreibung je Artist |
| `app/embeddings.py` | Embedding-Text und -Modell; `python -m app.embeddings` erzeugt die Embeddings aller Artists |
| `app/llm.py` | Generierte Antwort (Phase 2, in Arbeit): System-Prompt, Kontext aus den Suchtreffern, Ollama-Aufruf (`urllib`, Zeitlimit 60 s), Fehler als `LLMUnavailableError` |
| `static/` | `index.html`, `app.js`, erzeugtes `style.css` |
| `tests/` | `test_schedule.py`, `test_models.py`, `test_api.py`, `test_seed.py`, `test_embeddings.py`, `test_crud.py`, `test_search_api.py`, `test_llm.py`, `test_answer_api.py` (96 Tests) |

**API** (flacher JSON-Vertrag, `title`/`stage` als Strings):

- `GET /api/program?stage=&day=YYYY-MM-DD` → `{ now, items: [{id, title, stage, starts_at, ends_at, status}] }`
- `GET /api/stages` → Bühnennamen, alphabetisch
- `GET /api/days` → Tage mit Acts, chronologisch
- `GET /api/answer?q=` → generierte Antwort auf Basis derselben Suchtreffer (C12/B10, Phase 2):
  `{ status: "ok" | "no_hits" | "unavailable", answer }`, immer `200`; ohne Treffer kein
  LLM-Aufruf
- `GET /api/search?q=` → semantische Suche (B8/F11):
  `{ items: [{id, title, stage, day, starts_at, ends_at}] }`, `q` Pflicht und nicht leer

**Wichtige Regeln:**

- Zeitzone: fester Offset UTC+02:00, keine Sommerzeit-Logik. Zeitstempel werden naiv in
  Festival-Ortszeit gespeichert.
- „Jetzt" bestimmt der Server (`festival_now`, als FastAPI-Dependency, in Tests ersetzbar).
- Status wird **nach** Bühnen- und Tagesfilter berechnet.
- Ein Act gehört zu dem Tag, an dem er beginnt (auch wenn er nach Mitternacht endet).
- Keine Migrationen: Tabellen per `create_all`; das Seed-Skript löscht die Tabellen und legt
  sie neu an, so kommen Schemaänderungen in die Datenbank.

Details: [`architecture.md`](architecture.md).

## 4. Domain-/Datenmodell

Drei Entitäten, drei Tabellen:

```text
Artist (id, name, genre, description, embedding)   1 ── n  Act
Stage  (id, name unique)     1 ── n  Act
Act    (id, artist_id FK, stage_id FK, starts_at, ends_at)
```

- `ends_at > starts_at`, nicht leere Namen (`Artist`, `Stage`) sowie nicht leere `genre` und
  `description` (`Artist`) sind zusätzlich DB-seitig als `CheckConstraint` erzwungen.
- Nicht gespeichert, sondern zur Laufzeit berechnet: Status „now"/„next", Sortierung, Tage.
- Keine Entitäten für Festival, Tag, Nutzer oder Favoriten (Favoriten liegen nur im Browser).
- **Vektorsuche:** `genre` (Text), `description` (Text) und `embedding` (`vector(384)`,
  nullable) auf `Artist` sind angelegt. Das Embedding wird nur aus `name`, `genre` und
  `description` erzeugt und muss bei jeder Änderung dieser Felder neu berechnet werden; es ist
  für alle Artists gesetzt (per `python -m app.embeddings`). `Stage` und `Act` sind unverändert.

Details: [`domain-model.md`](domain-model.md).

## 5. Implementierte Features

- Programm als chronologische Liste (Zeit, Titel, Bühne), ohne Login (US-2).
- Hervorhebung „läuft jetzt" und „kommt als Nächstes", optisch unterscheidbar per Farbe und
  Text-Badge (US-3, US-4, T-22).
- Filter nach Bühne (US-5) und nach Tag, kombinierbar (US-8); bei schnellem Filterwechsel
  wird nur die Antwort auf die letzte Auswahl angezeigt (T-23).
- Mehrtägiges Programm, nach Tag gruppiert mit Überschrift wie „Fr, 18.09." (US-8).
- Acts als Favorit merken (Stern ☆/★), nur im Browser gespeichert (`localStorage`), bleibt
  über ein Neuladen erhalten (US-9).
- Persönlicher Zeitplan „Meine Favoriten" über dem Programm, als Akkordeon (beim Laden
  zugeklappt, Kopfzeile mit Anzahl): immer alle Favoriten
  chronologisch mit Tag, Zeit, Titel und Bühne, unabhängig vom Filter; Hinweis, solange
  keine Favoriten gemerkt sind (US-10).
- Responsive Oberfläche mit Tailwind CSS, ab 360 px ohne horizontales Scrollen (US-6, US-7).
- Semantische Suche nach Acts in eigenen Worten (Suchbereich über den Favoriten), sortiert
  nach Ähnlichkeit, unterstützt deutsche Anfragen, kein LLM (C11, F11, B8, B9, T4; US-11).
- Generierte Antwort zu einer Suche auf Knopfdruck („Antwort generieren"), nur aus den
  Suchtreffern, lokal per Ollama (`qwen3-instruct:4b`); Hinweis, wenn das LLM nicht verfügbar
  ist (C12, F12, B10, T5; Phase 2 – umgesetzt bis einschließlich Frontend, Halluzinationsschutz
  und Review stehen noch aus).
- Seed-Skript mit vier Festivaltagen ab heute, inkl. paralleler Acts und Acts über
  Mitternacht (US-1).
- Datenhaltung in PostgreSQL (Neon) mit Verbindungs-Check gegen Neons Idle-Suspend.

## 6. Aktueller Entwicklungsstand

- **v0.1** (US-1 bis US-6): umgesetzt, reviewt, freigegeben.
- **v0.2 Phase 1** (T-1 bis T-9): Umbau auf `Artist`/`Stage`/`Act` und Modulaufteilung –
  umgesetzt, freigegeben. Review-Punkte T-15 bis T-18 erledigt.
- **v0.2 Phase 2** (T-10 bis T-14): Umstellung SQLite → PostgreSQL (Neon) – umgesetzt,
  freigegeben. Review-Punkte T-19 bis T-21 erledigt.
- **v0.3:** US-7 (Tailwind, responsive) und US-8 (Tage gruppieren/filtern) umgesetzt,
  reviewt und freigegeben ([`review.md`](review.md), Abschnitt 8); Review-Punkte daraus
  (T-22 bis T-26) alle erledigt. US-9 (Favoriten merken) und US-10 (persönlicher Zeitplan)
  umgesetzt, reviewt und freigegeben (Abschnitt 9); die Darstellungspunkte daraus (T-27
  Aufklapp-Pfeil in Safari, T-28 Kontrast des Favoriten-Sterns) sind erledigt.
  Die übrigen v0.3-Anforderungen stehen im Entwurf von [`requirements.md`](requirements.md),
  sind aber noch nicht als Stories im Backlog. Die Festival-Entität ist bis auf Weiteres
  zurückgestellt.
- **Vektorsuche und LLM (neue Phase):** zwei getrennte Phasen; Phase 2 beginnt erst, wenn
  Phase 1 funktioniert und reviewt ist.
  **Phase 1 – abgeschlossen, reviewt, freigegeben (US-11, 2026-09-24).** Umsetzung in
  13 Roadmap-Schritten (Details: [`roadmap.md`](roadmap.md)): `Artist` um `genre`,
  `description`, `embedding` (`vector(384)`, pgvector) erweitert; Embeddings per
  `python -m app.embeddings` (`app/embeddings.py`, Modell
  `paraphrase-multilingual-MiniLM-L12-v2`); Suche in `app/crud.py`
  (`search_top_artists()`/`acts_for_artists()`/`search_acts()`, Top 5 Artists, unabhängig von
  Tages-/Bühnenfilter, auch vergangene Acts); Endpunkt `GET /api/search?q=`
  (`app/routers.py`); Frontend-Anbindung in `static/app.js` (Mock-Daten aus Schritt 1 entfernt).
  Review: [`review.md`](review.md) Abschnitt 10, „Freigeben mit nicht blockierenden
  Änderungswünschen", keine Blocker; T-29 (veraltete, ungenutzte Regel in
  `static/style.css`) ist erledigt; der zunächst fehlende Live-Browsertest ist am 2026-09-25
  per Headless Chrome nachgeholt.
  `Suchanfrage → Embedding-Modell → Query-Vektor → PostgreSQL/pgvector → passende Acts`, kein
  LLM, keine generierte Antwort.
  **Phase 2 – LLM/RAG: in Arbeit (Roadmap-Schritte 1–10 erledigt, 2026-09-25).**
  Anforderungen C12, F12, B10, T5 in [`requirements.md`](requirements.md): Antwort nur auf
  Knopfdruck („Antwort generieren") zu einer Suche mit Treffern, Kontext ausschließlich die
  Suchtreffer, bei LLM-Ausfall bleiben die Treffer sichtbar, kein Chat. LLM: `qwen3-instruct:4b`
  lokal über Ollama. Kontext: genau die Suchtreffer mit Name, Genre, Beschreibung, Bühne, Tag,
  Zeiten und serverseitig berechnetem Status „vorbei / läuft gerade / kommt noch"
  ([`architecture.md`](architecture.md), „Generierte Antwort"), als Klartext unter „Gefundene
  Acts:", ein nummerierter Block pro Act (Artist, Genre, Beschreibung, Bühne, Zeit, Status),
  Frage am Ende. System-Prompt als erster
  Entwurf (u. a. nur Kontext, nichts erfinden, Status beachten, Acts beim Namen, kurz auf
  Deutsch). Modell mit Mock-Kontext ausprobiert: nichts erfunden; vergangene Acts stehen im
  Kontext hinten (danach nicht mehr empfohlen), schwach passende Acts werden teils noch
  mitgenannt; Zeitlimit 60 s (Antworten 2–35 s). Code: `app/llm.py` baut aus echten
  Suchtreffern Kontext und Nachrichten (getestet); End-to-End gegen Neon + Ollama
  funktioniert; der Ollama-Aufruf samt Fehlerbehandlung ist im Backend (`generate_answer()`)
  und über `GET /api/answer?q=` erreichbar (erster Aufruf ca. 74 s wegen Modell-Laden, danach
  17–22 s). Frontend: Button „Antwort generieren" über der Trefferliste, im echten Browser
  (Headless Chrome, 360 px) geprüft.
  `Suchanfrage → Vektorsuche → passende Acts → LLM-Kontext → generierte Antwort`. Die
  Vektorsuche bleibt die Retrieval-Schicht; das LLM darf keine Festivalinformationen erfinden,
  die nicht in den gefundenen Daten stehen.
- Tests: `python -m pytest`, 96 grün (Stand 2026-09-25).

## 7. Offene Entscheidungen und bekannte Probleme

**Offene Anforderungsfragen (v0.3, vor der Umsetzung zu klären):**

- Offline-Nutzung (F10): Status „läuft jetzt/als Nächstes" offline clientseitig berechnen
  oder als veraltet kennzeichnen?
- Mehrere Festivals (C4): gilt UTC+02:00 für alle, oder eigene Zeitzone pro Festival?
- Import (B7): Datenformat, Endpunkt oder Skript, Art des Zugriffsschutzes?
- Festival-Entität (B5): gehört ein `Artist` zu einem Festival oder wird er geteilt?

**Offene Frage zur Vektorsuche** (Rest ist mit Phase 1 geklärt, siehe oben und
[`requirements.md`](requirements.md)):

- Wie bekommen importierte Artists (B7, noch nicht umgesetzt) ihr Embedding – automatisch beim
  Import oder per separatem Befehl wie nach dem Seed?

**Bekannte Einschränkungen:**

- Generierte Antwort (Phase 2, noch nicht umgesetzt): Das 4B-Modell nennt teils auch schwach
  passende Suchtreffer und hat im End-to-End-Test einem Act eine Eigenschaft angedichtet
  („Moonlight Session … mit Blasinstrumenten"); Acts, Bühnen und Zeiten hat es bisher nicht
  erfunden. Wird in Roadmap-Schritt 11 (Halluzinationsschutz) angegangen.

- Tests decken die PostgreSQL-spezifische Infrastruktur (URL-Normalisierung, psycopg) nicht
  ab, da sie gegen In-Memory-SQLite laufen; auch sie brauchen trotzdem eine gesetzte
  `DATABASE_URL`.
- Favoriten merken sich die Act-`id`. Das ist stabil, solange die Daten nur per Seed
  entstehen; mit einem Import (B7) kann eine gespeicherte `id` auf einen anderen Act zeigen.
- `domain-model.md` beschreibt noch „eine Instanz = ein Festival" (Stand v0.2); das passt
  nicht mehr zum v0.3-Entwurf mit mehreren Festivals und wird mit dessen Umsetzung angepasst.

## 8. Nächste geplante Schritte

1. Vektorsuche Phase 2 (LLM/RAG) nach [`roadmap.md`](roadmap.md) abschließen: Fehlerfälle
   und Halluzinationsschutz (Schritt 11, u. a. der Fall „Blasinstrumente"), Tests (Schritt 12),
   Review und Dokumentation (Schritt 13).
2. Offene Fragen des v0.3-Entwurfs klären (siehe Abschnitt 7).
3. Restliche v0.3-Anforderungen als User Stories ins Backlog übernehmen und priorisieren:
   - mehrere Festivals + Festivalauswahl (C4, C5, F5, B5, B6) – zurückgestellt,
   - Datenimport über einen geschützten Backend-Zugang (B7),
   - Offline-Verfügbarkeit (C9, F10).
4. Die Festival-Entität erfordert eine Erweiterung von Domain Model und Architektur (neue
   Entität, FKs von `Stage`/`Act`) – vor der Umsetzung dokumentieren.

Weitere Quellen: [`../CLAUDE.md`](../CLAUDE.md), [`requirements.md`](requirements.md),
[`backlog.md`](backlog.md), [`roadmap.md`](roadmap.md), [`review.md`](review.md).
