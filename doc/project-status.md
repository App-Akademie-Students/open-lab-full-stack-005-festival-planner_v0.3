# Projektstatus – Festival Planner

Stand: 2026-09-21. Kompakter Überblick über den aktuellen Stand, gedacht für externe
Gesprächspartner (z. B. ChatGPT), die das Projekt ohne Code und ohne alle Dokumente verstehen
sollen. Details stehen in den verlinkten Dokumenten unter `doc/`.

## 1. Projekt und Version

- **Name:** Festival Planner
- **Version/Phase:** v0.1 und v0.2 umgesetzt und reviewt. **v0.3 in Arbeit** – die
  Anforderungen liegen als Entwurf vor, vier neue Stories sind umgesetzt (US-7 bis US-10).
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

## 3. Architektur und Technologien

**Stack:** Python 3, FastAPI (uvicorn), SQLAlchemy, PostgreSQL bei Neon (Treiber `psycopg` v3,
Verbindung über `DATABASE_URL` in `.env` via `python-dotenv`), HTML + Vanilla JS (kein
JS-Framework, kein JS-Build), Tailwind CSS v4 (Standalone-CLI, erzeugtes CSS ist eingecheckt).
Tests: pytest + httpx (nur Dev), laufen gegen In-Memory-SQLite, nicht gegen Neon.

Ein Prozess (uvicorn) liefert API und Frontend aus. Flache Modulstruktur:

| Datei | Aufgabe |
|---|---|
| `app/main.py` | App-Objekt, Lifespan (`init_db()`), bindet Router und `static/` ein |
| `app/routers.py` | API-Endpunkte und Pydantic-Antwortmodelle |
| `app/crud.py` | Datenbank-Queries (Joins über `Artist`/`Stage`) |
| `app/schedule.py` | Reine Business-Logik: Festival-Zeit, Festivaltag, Status „now"/„next" |
| `app/models.py` | ORM-Modelle `Artist`, `Stage`, `Act` |
| `app/db.py` | Engine, Session, `init_db()`; bricht ohne `DATABASE_URL` mit klarer Meldung ab |
| `app/seed.py` | Seed-Skript: vier Festivaltage ab heute, 3 Bühnen |
| `static/` | `index.html`, `app.js`, erzeugtes `style.css` |
| `tests/` | `test_schedule.py`, `test_models.py`, `test_api.py`, `test_seed.py` (36 Tests) |

**API** (flacher JSON-Vertrag, `title`/`stage` als Strings):

- `GET /api/program?stage=&day=YYYY-MM-DD` → `{ now, items: [{id, title, stage, starts_at, ends_at, status}] }`
- `GET /api/stages` → Bühnennamen, alphabetisch
- `GET /api/days` → Tage mit Acts, chronologisch

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
Artist (id, name)            1 ── n  Act
Stage  (id, name unique)     1 ── n  Act
Act    (id, artist_id FK, stage_id FK, starts_at, ends_at)
```

- `ends_at > starts_at` und nicht leere Namen (`Artist`, `Stage`) sind zusätzlich DB-seitig
  als `CheckConstraint` erzwungen.
- Nicht gespeichert, sondern zur Laufzeit berechnet: Status „now"/„next", Sortierung, Tage.
- Keine Entitäten für Festival, Tag, Nutzer oder Favoriten (Favoriten liegen nur im Browser).

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
  umgesetzt, noch nicht reviewt.
  Die übrigen v0.3-Anforderungen stehen im Entwurf von [`requirements.md`](requirements.md),
  sind aber noch nicht als Stories im Backlog. Die Festival-Entität ist bis auf Weiteres
  zurückgestellt.
- Tests: `python -m pytest`, 36 grün (Stand 2026-09-21).

## 7. Offene Entscheidungen und bekannte Probleme

**Offene Anforderungsfragen (v0.3, vor der Umsetzung zu klären):**

- Offline-Nutzung (F10): Status „läuft jetzt/als Nächstes" offline clientseitig berechnen
  oder als veraltet kennzeichnen?
- Mehrere Festivals (C4): gilt UTC+02:00 für alle, oder eigene Zeitzone pro Festival?
- Import (B7): Datenformat, Endpunkt oder Skript, Art des Zugriffsschutzes?
- Festival-Entität (B5): gehört ein `Artist` zu einem Festival oder wird er geteilt?

**Bekannte Einschränkungen:**

- Tests decken die PostgreSQL-spezifische Infrastruktur (URL-Normalisierung, psycopg) nicht
  ab, da sie gegen In-Memory-SQLite laufen; auch sie brauchen trotzdem eine gesetzte
  `DATABASE_URL`.
- Favoriten merken sich die Act-`id`. Das ist stabil, solange die Daten nur per Seed
  entstehen; mit einem Import (B7) kann eine gespeicherte `id` auf einen anderen Act zeigen.
- `domain-model.md` beschreibt noch „eine Instanz = ein Festival" (Stand v0.2); das passt
  nicht mehr zum v0.3-Entwurf mit mehreren Festivals und wird mit dessen Umsetzung angepasst.

## 8. Nächste geplante Schritte

1. US-9 und US-10 (Favoriten, persönlicher Zeitplan) testen und reviewen.
2. Offene Fragen des v0.3-Entwurfs klären (siehe Abschnitt 7).
3. Restliche v0.3-Anforderungen als User Stories ins Backlog übernehmen und priorisieren:
   - mehrere Festivals + Festivalauswahl (C4, C5, F5, B5, B6) – zurückgestellt,
   - Datenimport über einen geschützten Backend-Zugang (B7),
   - Offline-Verfügbarkeit (C9, F10).
4. Die Festival-Entität erfordert eine Erweiterung von Domain Model und Architektur (neue
   Entität, FKs von `Stage`/`Act`) – vor der Umsetzung dokumentieren.

Weitere Quellen: [`../CLAUDE.md`](../CLAUDE.md), [`requirements.md`](requirements.md),
[`backlog.md`](backlog.md), [`roadmap.md`](roadmap.md), [`review.md`](review.md).
