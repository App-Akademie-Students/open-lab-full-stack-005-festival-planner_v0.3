# Festival Planner

## Project Goal

Wir entwickeln einen minimalistischen Festival-Planer für Festivalbesucher.
"Wo ist was wann?"

## Project Status

Phasen und Vorgehen: [`doc/roadmap.md`](doc/roadmap.md).
User Stories, Priorität und Status: [`doc/backlog.md`](doc/backlog.md).

Stand 2026-09-18: v0.1 (Roadmap-Schritt 9, User Stories US-1 bis US-6) ist umgesetzt. v0.2 ist
ebenfalls umgesetzt, in zwei Phasen: Refactoring Phase 1 (T-1 bis T-9) mit `Artist`, `Stage`,
`Act` als getrennten Entitäten und der Aufteilung in `models.py`, `db.py`, `crud.py`,
`schedule.py`, `routers.py`, `main.py`, `seed.py`; Refactoring Phase 2 (T-10 bis T-13) mit der
Umstellung der Datenbank von SQLite auf PostgreSQL (Neon). Testen und Reviewen
ist für beide Phasen erledigt und in `doc/review.md` freigegeben (Abschnitt 6 zu Phase 1,
Abschnitt 7 zur PostgreSQL-Umstellung), beide ohne Blocker. Die nicht blockierenden
Änderungswünsche daraus (T-15 bis T-21) sind alle umgesetzt.

v0.3 ist als Entwurf in `doc/requirements.md` aufgenommen. Davon umgesetzt: US-7 (responsive
Darstellung mit Tailwind CSS) und US-8 (Programm nach Tag gruppieren und filtern), beide in
`doc/review.md` (Abschnitt 8) ohne Blocker freigegeben; die Änderungswünsche daraus (T-22 bis
T-26) sind alle erledigt. Ebenfalls umgesetzt: US-9 (Acts als Favorit merken, nur im Browser)
und US-10 (persönlicher Zeitplan als Bereich „Meine Favoriten" über dem Programm).
Die übrigen v0.3-Anforderungen sind noch nicht im Backlog; die Festival-Entität ist bis auf
Weiteres zurückgestellt.

Ab Phase 2 gilt eine neue Leitlinie für die Architektur: nicht mehr „so klein wie möglich"
(MVP), sondern gut strukturiert und erweiterbar – die Struktur wächst Schritt für Schritt mit
der Komplexität, sobald ein konkreter Bedarf besteht. Details:
[`doc/architecture.md`](doc/architecture.md).
Nach jeder Story/Aufgabe den Status in `doc/backlog.md` aktualisieren.

## Tech Stack

* Python 3
* FastAPI, gestartet über uvicorn
* SQLAlchemy
* PostgreSQL (gehostet bei Neon), Treiber `psycopg` (v3)
* HTML + Tailwind CSS (v4, CSS wird mit der Tailwind-CLI erzeugt – einziger Build-Schritt)
* Vanilla JavaScript – kein JS-Framework, kein JS-Build

Nur für die Entwicklung (bewusste Ausnahme von T1 in `doc/requirements.md`):

* pytest
* httpx (wird von FastAPIs `TestClient` benötigt)

## Project Decisions

* **Festival-Zeitzone (T3):** fester Offset UTC+02:00. Keine Sommer-/Winterzeit-Logik und
  damit keine zusätzliche Dependency (`tzdata` wäre unter Windows für `zoneinfo` nötig).
  Für ein Festival über wenige aufeinanderfolgende Tage ausreichend.
* **Tests:** pytest + httpx ausschließlich als Dev-Dependencies, nicht für den Betrieb.
* **Sprache:** Projektdokumentation (`doc/`, README) auf Deutsch; Code (Bezeichner,
  Kommentare, Docstrings) auf Englisch.
* **Datenbank (v0.2):** PostgreSQL bei Neon statt SQLite. `DATABASE_URL` liegt in `.env`
  (nicht eingecheckt, siehe `.gitignore`) und wird in `db.py` per `python-dotenv` geladen.
  Treiber ist `psycopg` (v3); eine `postgresql://`-URL wird in `db.py` automatisch auf
  `postgresql+psycopg://` normalisiert, da SQLAlchemy sonst `psycopg2` erwartet, das nicht
  installiert ist. Datenintegrität `ends_at > starts_at` wird zusätzlich als DB-seitige
  `CheckConstraint` auf `Act` erzwungen, nicht nur in der Business-Logik.
  Fehlt `DATABASE_URL`, bricht `db.py` mit einer erklärenden `RuntimeError`-Meldung ab (kein
  stiller Fallback). Die Engine nutzt `pool_pre_ping=True`, weil Neon die Compute-Instanz im
  Leerlauf herunterfährt und sonst der erste Request nach einer Pause an einer toten
  Pool-Verbindung scheitert.
  Tests laufen weiterhin gegen eine In-Memory-SQLite-DB (`tests/test_api.py`,
  `tests/test_models.py`), nicht gegen Neon.
* **Tailwind CSS (v0.3, US-7):** Quelle ist `tailwind/input.css`, die Tailwind-CLI erzeugt
  daraus `static/style.css` (minifiziert). Die erzeugte Datei ist **eingecheckt**, damit die App
  ohne Tailwind-CLI, Node oder Build-Schritt startet (T2) – die CLI braucht nur, wer das
  Frontend ändert. Verwendet wird das **Standalone-Binary** der Tailwind-CLI (kein Node/npm);
  es liegt nicht eingecheckt im Projektordner (siehe `.gitignore`). Nur Klassennamen aus
  `static/` werden erkannt; in `app.js` gesetzte Klassen müssen deshalb vollständig
  ausgeschrieben sein (kein Zusammensetzen wie `` `bg-${color}-50` ``).

## Functional Requirements

Die Anforderungen (Muss / optional / Benutzeraktionen / Scope-Abgrenzung) sind in
[`doc/requirements.md`](doc/requirements.md) definiert.

Kurzfassung (umgesetzter Stand): Ein Festival über einen oder mehrere Tage, Programm als
chronologische Liste, nach Tag gruppiert, Filter nach Tag und Bühne, Anzeige „läuft jetzt /
kommt als Nächstes", responsive mit Tailwind CSS, Favoriten im Browser (`localStorage`) mit
persönlichem Zeitplan über dem Programm. Daten per Seed, kein Login.
Weitere v0.3-Anforderungen (mehrere Festivals, Import, Offline) sind in
`doc/requirements.md` als Entwurf aufgenommen, aber noch nicht umgesetzt.

## Architecture

Vollständig in [`doc/architecture.md`](doc/architecture.md).

Kurzfassung – Leitlinie seit Phase 2: nicht mehr „so klein wie möglich", sondern gut
strukturiert und erweiterbar; die Struktur wächst Schritt für Schritt mit der Komplexität,
sobald ein konkreter Bedarf besteht (nicht spekulativ auf Vorrat):

| Bereich | Ort |
|---|---|
| API (`GET /api/program?stage=&day=`, `GET /api/stages`, `GET /api/days`) | `app/routers.py` |
| App-Objekt, Lifespan, bindet Router + `static/` ein | `app/main.py` |
| Datenbank-Infrastruktur: Engine (PostgreSQL/Neon, `DATABASE_URL` aus `.env`), Session, `init_db()` | `app/db.py` |
| ORM-Modelle `Artist`, `Stage`, `Act` | `app/models.py` |
| Datenbank-Queries (Joins über `Artist`/`Stage`) | `app/crud.py` |
| Business-Logik: Festival-Zeit, Festivaltag, Status „now" / „next" (reine Funktionen, ohne DB/HTTP) | `app/schedule.py` |
| Seed-Skript (vier Festivaltage ab dem heutigen Datum) | `app/seed.py` |
| Frontend (HTML/Vanilla JS, erzeugtes `style.css`) | `static/` |
| Tailwind-Quelle für `static/style.css` | `tailwind/input.css` |
| Tests | `tests/` |

Kernregeln:

* Queries stehen in `crud.py`, nicht direkt in den Endpunkten.
* Der Status wird **nach** dem Bühnen- und Tagesfilter berechnet.
* Ein Act gehört zu dem Tag, an dem er beginnt (auch wenn er nach Mitternacht endet).
* Zeitstempel werden naiv in Festival-Ortszeit (UTC+02:00) gespeichert.
* Die Business-Logik bekommt `now` als Parameter; `festival_now` ist in `schedule.py`
  definiert und wird in `routers.py` als FastAPI-Dependency verwendet; Tests ersetzen sie per
  `dependency_overrides`.
* Aktuell noch nicht vorhanden, aber kein grundsätzliches Verbot mehr: `schemas.py`,
  `services/`, Repository-Klassen, Paket-Split (`app/api/`, `app/domain/`, …) – kommen, sobald
  ein konkreter Bedarf entsteht. Bedingungen dafür: [`doc/architecture.md`](doc/architecture.md).

## Domain Model

Vollständig in [`doc/domain-model.md`](doc/domain-model.md).

Kurzfassung: Drei Entitäten `Artist`, `Stage`, `Act` (statt einer flachen
`ProgramItem`-Tabelle). `Act` referenziert `Artist` und `Stage` per Fremdschlüssel und trägt
`starts_at`/`ends_at`. Die API liefert weiterhin flache `title`/`stage`-Strings, befüllt aus
den Beziehungen (Entscheidung siehe `architecture.md`).
„Läuft jetzt / kommt als Nächstes", Sortierung und Bühnenliste werden zur Laufzeit berechnet
bzw. abgeleitet. Keine Festival- oder User-Entität im Domain Model.

## Development Rules

* Let the application grow in complexity step by step; introduce new structure (files,
  packages, layers) only when a concrete need justifies it, not speculatively.
* Do not add unnecessary frameworks or dependencies.
* Analyze requirements before implementing changes.
* Keep the existing project structure and coding style consistent.
* Write simple, readable code.
* Add tests for important business logic.
* Document important decisions and non-obvious code.
* Review existing code before making larger changes.

## Working with Claude

* Analyze the existing project before making changes.
* Prefer small, incremental changes.
* Explain larger structural changes before implementing them.
* Do not introduce new dependencies without a clear reason.
* Do not implement functionality that is not part of the agreed requirements.
* Ask for clarification when requirements are ambiguous.
* Update this file when important project decisions change.

## Project Commands

Alle Befehle im Projektordner mit aktivierter virtueller Umgebung.

### Create and activate virtual environment

```bash
python -m venv .venv
```

* Windows PowerShell: `.venv\Scripts\Activate.ps1`
* macOS / Linux: `source .venv/bin/activate`

### Install dependencies

```bash
pip install -r requirements.txt       # Betrieb
pip install -r requirements-dev.txt   # Entwicklung inkl. pytest + httpx
```

`requirements-dev.txt` wird mit dem ersten Code angelegt.

### Configure database connection

`.env` im Projektordner anlegen (nicht eingecheckt) mit:

```
DATABASE_URL=postgresql://<user>:<password>@<host>/<db>?sslmode=require
```

Verbindungsdaten kommen aus dem Neon-Projekt.

### Build CSS (nur bei Änderungen am Frontend)

Einmalig das Tailwind-CLI-Standalone-Binary für die eigene Plattform von
<https://github.com/tailwindlabs/tailwindcss/releases> (v4) herunterladen und als
`tailwindcss.exe` (Windows) bzw. `tailwindcss` (macOS/Linux, ausführbar machen) in den
Projektordner legen. Danach:

```bash
./tailwindcss -i tailwind/input.css -o static/style.css --minify           # einmalig
./tailwindcss -i tailwind/input.css -o static/style.css --watch            # während der Entwicklung
```

Die erzeugte `static/style.css` wird mit eingecheckt.

### Seed database

```bash
python -m app.seed
```

Löscht die Tabellen in der über `DATABASE_URL` konfigurierten PostgreSQL-Datenbank, legt sie
neu an (so kommen auch Schemaänderungen wie neue Constraints an) und füllt das Programm für vier Tage ab dem heutigen Datum.

### Start backend

```bash
uvicorn app.main:app --reload
```

Danach im Browser: <http://127.0.0.1:8000> (API-Doku: <http://127.0.0.1:8000/docs>).

### Run tests

```bash
python -m pytest
```

`python -m` statt nur `pytest`, damit das Projektverzeichnis im Importpfad liegt.

## Teaching Material

Files in `teaching/` are intended for participants only.

Do not read, analyze, summarize, or use files from this directory unless the user explicitly asks for it.

For you teaching/ is write only. When ever you think you have interesting information for teaching you can add it to teaching/


## Requirements Policy

`doc/requirements.md` represents the current required
behavior of the system.

When requirements change:

- update the current requirements instead of appending
  historical changes;
- remove requirements that are no longer valid;
- do not document implementation details as requirements;
- preserve important previous milestone specifications
  as snapshots under `doc/requirements-history/`;
- use Git history for detailed change history.
## Project Status Maintenance

Keep `doc/project-status.md` up to date.

Update this file whenever a relevant project change affects one or more of the following:

* project goal or current phase
* architecture or technology stack
* domain/data model
* implemented features
* current development status
* open decisions or known issues
* next planned steps

Do not update it for trivial changes such as formatting, comments, renaming local variables, or other changes that do not affect the overall project state.

The file should always represent the current state of the project, not a detailed change history.

Keep it concise and understandable for an external reader who does not have to inspect the complete codebase.
