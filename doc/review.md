# Backend-Review – Festival Planner

Stand: 2026-09-11. Unabhängiges Code-Review von `app/main.py`, `app/db.py`, `app/schedule.py`,
`app/seed.py` und den zugehörigen Tests gegen `CLAUDE.md`, `doc/requirements.md`,
`doc/domain-model.md`, `doc/architecture.md` und `doc/backlog.md`.

**Hinweis vorab:** `app/models.py` existiert nicht. Das Datenmodell `ProgramItem` sowie
Engine/Session/`init_db()`/`get_db()` liegen – wie in `doc/architecture.md` vorgesehen – in
`app/db.py`. Geprüft wurde stattdessen `app/db.py`, zusammen mit `app/main.py`,
`app/schedule.py`, `app/seed.py`, `tests/test_api.py` und `tests/test_schedule.py`. Zur
Verifikation wurde lesend `python -m pytest -q` im Projekt ausgeführt: **14 passed** (2 harmlose
Deprecation-Warnings zu `httpx`/`anyio`, keine Fehler).

## 1. Erfüllung der Akzeptanzkriterien

**T-0 · Projektgerüst — erfüllt.** Ordnerstruktur entspricht `architecture.md`;
`app/__init__.py` ist leer und macht `app/` zum Package; `requirements-dev.txt` enthält pytest +
httpx; `python -m pytest` läuft grün (verifiziert).

**US-1 · Programm einspielen — erfüllt.** `app/seed.py` legt 14 Programmpunkte auf 3 Bühnen an
(im geforderten Rahmen 10–15), alle auf `festival_now().date()`, also dem heutigen Datum in
Festival-Zeit. Parallele Acts auf unterschiedlichen Bühnen sind vorhanden, ebenso mindestens
zwei Acts mit identischer Startzeit (`Opener Band` und `Folk Trio`, je 12:00). Alle Einträge
erfüllen `ends_at > starts_at`, Titel/Bühne nicht leer. Erneutes Ausführen löscht vorher alle
Zeilen (`db.query(ProgramItem).delete()`) und fügt neu ein – keine Duplikate.

**US-2 · Programm als Liste sehen — erfüllt.** `GET /api/program` sortiert per
`ORDER BY starts_at, stage` (`app/main.py:49`), identisch zur Doku. Frontend zeigt Start/Ende
(HH:MM), Titel, Bühne ohne Login. Leere Liste wird im Frontend über `#empty-hint` abgefangen
(`static/app.js:31`). Funktional erfüllt, inzwischen auch automatisiert getestet (siehe
Abschnitt 3 / Nachtrag).

**US-3 · Sehen, was gerade läuft — erfüllt.** Grenzfälle (`starts_at == now` → „now",
`ends_at == now` → nicht mehr „now", mehrere gleichzeitig) sind in `tests/test_schedule.py`
exakt abgedeckt und bestehen. `now` kommt serverseitig aus `festival_now()` (UTC+02:00, naiv)
und wird im JSON sowie im Frontend (`#now-hint`) angezeigt. Kein Auto-Refresh (Scope korrekt
eingehalten).

**US-4 · Sehen, was als Nächstes kommt — erfüllt.** Frühester Startzeitpunkt nach `now`, inkl.
Ties, korrekt in `compute_statuses` (`app/schedule.py:17-36`) und durch
`test_multiple_items_with_same_next_start_time` getestet. Vor Festivalbeginn nur „next", kein
„now" (`test_before_festival_start_only_next_no_now`); nach dem letzten Act nichts markiert,
kein Fehler (`test_after_last_item_nothing_highlighted`). Optisch unterscheidbar via
CSS-Klassen `status-now`/`status-next` mit unterschiedlichen Farben.

**US-5 · Nach Bühne filtern — erfüllt.** `GET /api/stages` liefert alphabetisch sortierte,
distincte Bühnen (`app/main.py:39`); Frontend baut daraus das Dropdown inkl. „Alle Bühnen".
`GET /api/program?stage=X` filtert serverseitig, unbekannte Bühne liefert leere Liste
(getestet). Status wird **nach** dem Filter berechnet (Filter zuerst in der Query, danach
`compute_statuses(items, now)` auf der bereits gefilterten Liste, `app/main.py:49-54`) – korrekt
und durch `test_next_is_computed_within_given_items_only` sinngemäß abgesichert.

**US-6 · Programm auf dem Smartphone nutzen — erfüllt** (soweit anhand des Codes beurteilbar;
kein visueller Browsertest bei 360 px durchgeführt). `static/style.css` verwendet
`box-sizing: border-box`, Flex-Wrap, relative Einheiten, kein festbreites Element über
Viewport-Breite hinaus; kein Build-Tooling, reines HTML/CSS/Vanilla JS.

## 2. Code-Review-Findings

- ✅ **Zeitzonen-Handling korrekt.** `festival_now()` (`app/schedule.py:12-14`) nutzt
  `datetime.now(FESTIVAL_TZ).replace(tzinfo=None)` – das liefert korrekt die aktuelle
  Wanduhrzeit in UTC+02:00 als naives Datetime, exakt konsistent mit den naiv in
  Festival-Ortszeit gespeicherten `starts_at`/`ends_at`. Das ist eine Stelle, an der leicht
  Fehler passieren (z. B. `utcnow()` + falscher Offset, oder Systemzeitzone statt fixem
  Offset) – hier ist es richtig gelöst.
- ✅ **`festival_now` als Funktion und als FastAPI-Dependency.** `app/seed.py` ruft
  `festival_now()` direkt auf, `app/main.py` nutzt sie über `Depends(festival_now)`
  (`app/main.py:47`). Da es sich um dieselbe Funktionsreferenz aus `app.schedule` handelt,
  funktioniert `app.dependency_overrides[festival_now] = ...` in `tests/test_api.py` wie in der
  Architektur beschrieben – durch den grünen Testlauf (`test_program_includes_status_and_now`
  erwartet exakt den überschriebenen Zeitpunkt) verifiziert.
- ✅ **Status wird nach dem Bühnenfilter berechnet**, wie in `architecture.md` gefordert
  (`app/main.py:49-54`).
- ✅ **Threadsafety SQLite.** `connect_args={"check_same_thread": False}` in `app/db.py:9`, mit
  Begründung im Kommentar exakt wie in der Architektur dokumentiert.
- ✅ **Kein Scope-Creep.** main.py enthält nur die zwei dokumentierten Endpunkte + Static-Mount +
  Lifespan; `schedule.py` nur `FESTIVAL_TZ`, `festival_now`, `compute_statuses`; keine
  zusätzlichen Felder (Genre, Beschreibung), keine Konflikterkennung, kein Tagesfilter, keine
  Suche/Favoriten. Entspricht `CLAUDE.md` ("Do not implement functionality that is not part of
  the agreed requirements").
- ⚠️ **Änderungswunsch – Fragile Test-Isolation in `tests/test_api.py`.**
  `app.dependency_overrides[get_db]` und `[festival_now]` werden auf Modulebene gesetzt (Zeilen
  35, 38), nicht in einer Fixture mit Teardown. Aktuell unproblematisch, da es das einzige
  Testmodul mit Overrides ist, aber sobald ein weiteres Testmodul dieselbe `app`-Instanz
  importiert, "leaken" diese Overrides prozessweit. Empfehlung (kein Blocker): Overrides in eine
  `autouse`-Fixture mit `app.dependency_overrides.clear()` im Teardown verschieben, falls das
  Projekt wächst.
- ⚠️ **Änderungswunsch – Domain-Invarianten nicht technisch erzwungen.**
  `doc/domain-model.md` nennt als Invarianten „title/stage nicht leer" und
  „ends_at > starts_at". In `app/db.py:14-21` gibt es dafür kein `CheckConstraint`, keine
  Validierung – nur `nullable=False`. Da es keine Schreib-API gibt (Daten kommen ausschließlich
  aus dem kontrollierten Seed-Skript), ist das Risiko im MVP gering, aber es ist eine Lücke
  zwischen dokumentierter Invariante und tatsächlicher Durchsetzung. Kein Blocker, aber
  erwähnenswert.
- ⚠️ **Änderungswunsch (sehr geringe Relevanz) – relative Pfade CWD-abhängig.**
  `DATABASE_URL = "sqlite:///./festival.db"` (`app/db.py:5`) und
  `StaticFiles(directory="static", ...)` (`app/main.py:69`) sind relativ zum Arbeitsverzeichnis.
  Funktioniert exakt wie in `CLAUDE.md`/`architecture.md` dokumentiert (`uvicorn` wird im
  Projektordner gestartet), ist also kein Fehler, nur ein impliziter Kontrakt ohne Fallback –
  für dieses MVP akzeptabel.
- ✅ **Keine Findings zu Sortierung/Filter/Serialisierung.** JSON-Format (`now`,
  `items[].status` als `"now"`/`"next"`/`null`, naive ISO-Zeitstempel ohne Offset) stimmt exakt
  mit dem in `architecture.md` dokumentierten Beispiel überein (durch Test
  `test_program_includes_status_and_now` mit `"2026-09-11T14:00:00"` verifiziert).

Keine ❌-Blocker gefunden.

## 3. Fehlende oder unzureichende Tests

- ~~Kein Test für „leere Datenbank" auf API-Ebene.~~ **Nachtrag:** Dieser Punkt wurde inzwischen
  behoben – `tests/test_api.py::test_program_and_stages_with_empty_database` prüft jetzt
  `GET /api/program` und `GET /api/stages` gegen eine leere Tabelle (leere Liste, kein Fehler).
  Suite läuft mit 15 Tests grün.
- Kleinere Lücke: `compute_statuses([], now)` (komplett leere Liste) ist nicht explizit getestet,
  obwohl das Verhalten trivial korrekt ist (leere Liste zurück).
- Ansonsten ist die Testabdeckung der Grenzfälle in `tests/test_schedule.py` sehr gut: exakter
  Start-/Endzeitpunkt, mehrere gleichzeitige „now", mehrere gleichzeitige „next" bei Tie, Status
  vor Festivalbeginn, Status nach letztem Act, sowie „next" nur innerhalb der übergebenen
  (gefilterten) Liste.
- `tests/test_api.py` deckt Sortierung, Statusfeld inkl. `now`, Bühnenfilter, unbekannte Bühne,
  Bühnenliste, Auslieferung von `index.html` und (neu) leere Datenbank ab – entspricht der in
  `architecture.md` beschriebenen Minimalabdeckung für die API-Schicht.

## 4. Abweichungen von Requirements, Domain Model, Architektur oder CLAUDE.md

Keine inhaltlichen Abweichungen gefunden. Im Detail geprüft und bestätigt konsistent:

- Tech-Stack exakt wie in `CLAUDE.md`/T1 (fastapi, uvicorn[standard], sqlalchemy; pytest+httpx
  nur in `requirements-dev.txt`).
- Dateiaufteilung entspricht 1:1 der Tabelle in `architecture.md` (inkl. der bewussten
  Abwesenheit von `routers/`, `schemas.py`, `crud.py`, `services/`).
- Sprache: Doku (`doc/`) Deutsch, Code (Docstrings/Kommentare) Englisch – eingehalten.
- `.gitignore` schließt `*.db`/`*.sqlite*` aus, wie in `architecture.md` verlangt.
- Domain Model exakt eine Entität `ProgramItem` mit den fünf dokumentierten Feldern, keine
  zusätzlichen Entitäten.
- Kein Tagesfilter, keine Mehrsprachigkeit, kein Login, keine Admin-UI – Scope-Abgrenzung aus
  `requirements.md` eingehalten.

## 5. Gesamturteil

**Freigeben mit (nicht blockierenden) Änderungswünschen.**

Die Implementierung erfüllt alle Akzeptanzkriterien von T-0 und US-1 bis US-6 fachlich korrekt,
inklusive der kritischen Grenzfälle bei Zeitzonen und Status-Berechnung. Der Code ist klein,
lesbar, konsistent mit der dokumentierten Architektur und ohne Scope-Creep. Keine Blocker. Der
ursprünglich empfohlene Nachtrag (Test für leere Datenbank) ist bereits umgesetzt. Die
verbleibenden ⚠️-Punkte (Test-Isolation der Dependency-Overrides, fehlende DB-seitige
Durchsetzung der Domain-Invarianten, CWD-abhängige Pfade) können als Backlog-Notiz für später
festgehalten werden, ohne die aktuelle Freigabe zu verzögern.

## 6. Nachtrag – Refactoring Phase 1 (v0.2, T-1 bis T-9), Stand 2026-09-16

Unabhängiges Review des abgeschlossenen Refactorings (Backlog `doc/backlog.md`, Abschnitt
„v0.2 – Refactoring Phase 1“) gegen `doc/domain-model.md` und `doc/architecture.md`. Geprüft:
`app/models.py`, `app/db.py`, `app/crud.py`, `app/routers.py`, `app/main.py`, `app/seed.py`,
`tests/test_api.py`. Verifiziert mit `python -m pytest -v`: **15 passed**, keine Fehler (dieselben
2 harmlosen Deprecation-Warnings wie zuvor). Zusätzlich manuell gegen eine frisch geseedete
SQLite-DB und einen laufenden `uvicorn`-Prozess geprüft (`/api/stages`, `/api/program?stage=…`,
`/`).

### Erfüllung der Akzeptanzkriterien T-1 – T-9

Alle neun Teilaufgaben sind erfüllt und entsprechen dem dokumentierten Zielbild:

- **T-1/T-2/T-3** – `app/models.py` enthält exakt `Artist`, `Stage`, `Act` mit den in
  `domain-model.md` spezifizierten Feldern, FKs und `relationship()`-Paaren
  (`back_populates` beidseitig korrekt gesetzt).
- **T-4** – API-Vertrag bleibt flach; dokumentiert inkl. verworfener Alternative in
  `architecture.md`.
- **T-5** – `app/seed.py` legt pro Slot einen `Act` mit `artist=Artist(...)` und einer pro
  Bühnenname **geteilten** `Stage`-Instanz an (`build_acts`, Zeilen 32–34) – SQLAlchemy
  kaskadiert die Inserts von `Artist`/`Stage` vor `Act` automatisch beim `add_all`. Löschreihenfolge
  vor dem Neu-Einfügen ist FK-korrekt (`Act` → `Artist` → `Stage`).
- **T-6** – `app/crud.py`: `list_stages` liefert die sortierte Namensliste, `list_program` joint
  `Act` auf `Artist`/`Stage`, sortiert nach `starts_at, Stage.name`, filtert optional. Die Query
  selektiert die Spalten bereits umbenannt (`Artist.name.label("title")`,
  `Stage.name.label("stage")`) – das erfüllt exakt die in `architecture.md` verlangte
  Flach-Umsetzung „`crud.py` muss die Umbenennung vornehmen“.
- **T-7** – `app/routers.py` enthält die zwei Endpunkte 1:1 wie zuvor in `main.py`, unverändertes
  Response-Format; `app/main.py` ist auf App-Objekt, `lifespan`/`init_db`, `include_router` und
  Static-Mount reduziert – keine Endpunkte mehr darin.
- **T-8** – `tests/test_api.py`-Fixtures legen jetzt `Stage`/`Artist`/`Act`-Zeilen an; die
  Testfälle selbst (Sortierung, Statusfeld, Filter, unbekannte Bühne, leere DB) sind unverändert
  und bestehen weiterhin.
- **T-9** – `app/db.py` enthält nur noch Engine, `SessionLocal`, `Base`, `init_db()`, `get_db()`;
  `ProgramItem` und die dafür nötigen Column-Importe sind entfernt. Frisch geseedete DB enthält
  ausschließlich die Tabellen `artists`, `stages`, `acts` (verifiziert).

### Findings

- ✅ **API-Vertrag unverändert** – live geprüft: `GET /api/program` und `GET /api/stages` liefern
  weiterhin flache `title`/`stage`-Strings, `static/app.js` musste nicht angepasst werden.
- ✅ **Kein Scope-Creep** – keine `schemas.py`, keine `services/`, keine Repository-Klassen;
  `crud.py` bleibt bei einfachen Funktionen, wie in `architecture.md` festgelegt.
- ✅ **Statusberechnung nach Filter weiterhin korrekt** – `routers.py` ruft `crud.list_program(db,
  stage=stage)` **vor** `compute_statuses(rows, now)` auf; Reihenfolge entspricht der
  dokumentierten Regel.
- ⚠️ **Änderungswunsch – TODO widerspricht dokumentierter Entscheidung.**
  `app/routers.py:15` trägt einen Kommentar `# TODO move to rest_schema.py` auf
  `ProgramItemOut`. `architecture.md` legt aber explizit fest: „Bewusst weggelassen: `schemas.py`
  … Pydantic-Antwortmodelle bleiben in `routers.py`“. Aktuell nur ein Kommentar, keine
  Funktionsänderung – aber falls das umgesetzt werden soll, ist das eine Architekturentscheidung,
  die zuerst in `architecture.md` und `CLAUDE.md` nachgezogen werden müsste, nicht nur im Code.
  Empfehlung: TODO entfernen oder bewusst als neue Entscheidung dokumentieren.
- ⚠️ **Weiterhin offen (aus Abschnitt 2 oben, unverändert durch das Refactoring):**
  Domain-Invarianten (`name` nicht leer, `ends_at > starts_at`) sind auf `Artist`/`Stage`/`Act`
  weiterhin nur über `nullable=False` abgesichert, nicht per `CheckConstraint`; Test-Overrides in
  `tests/test_api.py` weiterhin auf Modulebene statt in einer Fixture mit Teardown; `DATABASE_URL`
  und `StaticFiles`-Pfad weiterhin CWD-relativ. Alle drei unverändert nicht blockierend.
- ⚠️ **Kosmetisch, kein Blocker:** doppelte Leerzeile in `app/crud.py` (nach den Importen);
  ungenutzter `app`-Parameter in `main.py`s `lifespan(app: FastAPI)` (bereits seit v0.1 so, jetzt
  von Pylance markiert).

### Gesamturteil (Nachtrag)

**Freigeben.** Die Migration von `ProgramItem` zu `Artist`/`Stage`/`Act` ist vollständig,
funktional gleichwertig (API-Vertrag, Frontend, Zeitzonen- und Statusregeln unverändert) und
durch die grüne Testsuite sowie manuelle Live-Prüfung abgesichert. Einziger nennenswerter neuer
Punkt ist das TODO in `routers.py`, das der dokumentierten „kein `schemas.py`“-Entscheidung
widerspricht und vor einer Umsetzung geklärt werden sollte. Keine Blocker für Roadmap-Schritt 22.

## 7. Nachtrag – Refactoring Phase 2: Umstellung auf PostgreSQL (v0.2, T-10 bis T-13), Stand 2026-09-18

Unabhängiges Review der Datenbank-Umstellung (Backlog `doc/backlog.md`, Abschnitt „v0.2 –
Refactoring Phase 2") gegen `doc/requirements.md` (B2, T1), `doc/architecture.md` (Abschnitt
„Datenbank") und die Entscheidung in `CLAUDE.md`. Geprüfter Änderungsumfang ist der Commit
`77d7b0e`: `app/db.py`, `app/models.py`, `requirements.txt` – sonst kein Produktivcode.

Verifikation:

* `python -m pytest` – **15 passed** (dieselben 2 harmlosen Deprecation-Warnings wie zuvor).
* Lesende Live-Prüfung gegen die konfigurierte Neon-Datenbank (nur `SELECT`, kein DDL, keine
  Writes): Serverversion PostgreSQL 18.6, Tabellen `acts`, `artists`, `stages`,
  `ck_acts_ends_after_starts` in `pg_constraint` vorhanden, `acts.starts_at` ist
  `timestamp without time zone`, `acts.id` hat `nextval('acts_id_seq')` als Default.
* Messungen gegen dieselbe Datenbank: `init_db()` beim Kaltstart 0,39 s;
  `crud.list_program` 21–53 ms, `crud.list_stages` 18–30 ms (je 5 Läufe).

### Erfüllung der Akzeptanzkriterien T-10 bis T-13

- **T-10 – erfüllt.** `app/db.py:8-10` lädt `.env` per `load_dotenv()` und liest
  `DATABASE_URL`; im Code steht keine Verbindung mehr fest verdrahtet (B2). `.env` ist per
  `.gitignore:14` ausgeschlossen, **nicht** getrackt und war auch nie committed (geprüft mit
  `git ls-files .env` und `git log --all -- .env`, beide leer) – es liegt also kein Zugangsdatum
  in der Git-History.
- **T-11 – erfüllt.** `app/db.py:12-13` normalisiert eine `postgresql://`-URL auf
  `postgresql+psycopg://`. Die Umsetzung ist minimal und präzise: der `startswith`-Guard und
  `replace(..., 1)` lassen eine bereits explizite `postgresql+psycopg://`-URL sowie
  `sqlite://`-URLs unangetastet. Live verifiziert: die `.env` enthält die kurze Form (kein
  Treffer für `postgresql+psycopg`), die Engine verbindet sich trotzdem über psycopg 3.3.5.
- **T-12 – erfüllt.** `app/models.py:39-41` erzwingt `ends_at > starts_at` als
  `CheckConstraint`; in der Live-Datenbank ist `ck_acts_ends_after_starts` angelegt. Damit ist
  der ⚠️-Punkt „Domain-Invarianten nicht technisch erzwungen" aus Abschnitt 2 für die
  Zeitinvariante erledigt (für `Artist.name`/`Stage.name` weiterhin offen, siehe T-18).
- **T-13 – erfüllt.** `requirements.md` (B2, T1), `domain-model.md`, `architecture.md`,
  `CLAUDE.md`, `backlog.md` und `roadmap.md` nennen jetzt durchgängig PostgreSQL; die
  SQLite-Fassung von B2/T1 bleibt über `requirements-history/requirements-v0.1-mvp.md`
  nachvollziehbar.

### Findings

- ✅ **`check_same_thread` korrekt entfernt.** Das war eine reine SQLite-Eigenheit. Nicht nur
  überflüssig, sondern ein echter Fehler, wäre es stehen geblieben – verifiziert: mit
  `connect_args={"check_same_thread": False}` antwortet der Treiber mit
  `psycopg.ProgrammingError: invalid connection option "check_same_thread"`. Die Zeile musste
  also weg, und der zugehörige Kommentar ist konsequent mitentfernt worden.
- ✅ **Zeitmodell unverändert.** Die Spalten sind `DateTime` ohne `timezone=True` und landen in
  PostgreSQL als `timestamp without time zone` (live geprüft). Damit gilt die dokumentierte
  Regel „naiv in Festival-Ortszeit" unverändert und es gibt keine implizite Umrechnung – die
  Stelle, an der eine solche Migration am ehesten stillschweigend Zeiten verschiebt, ist
  richtig gelöst.
- ✅ **Kein Scope-Creep, API-Vertrag unverändert.** `models.py` (außer dem `CheckConstraint`),
  `crud.py`, `routers.py`, `schedule.py`, `main.py`, `seed.py` und `static/` sind im
  Migrations-Commit nicht angefasst; Response-Format und Frontend bleiben gleich. Die
  Umstellung ist damit tatsächlich auf die Infrastrukturschicht begrenzt, wie in
  `architecture.md` vorgesehen.
- ✅ **Keine Altlasten in der Zieldatenbank.** Die Neon-Datenbank enthält ausschließlich
  `artists`, `stages`, `acts` – keine Reste einer `program_items`-Tabelle.
- ✅ **Verbindung ist TLS-verschlüsselt.** Client-seitig meldet psycopg `ssl_in_use = True`.
  Nicht offensichtlich und leicht als Fehlalarm zu lesen: `pg_stat_ssl` meldet für dieselbe
  Verbindung `ssl = false`, weil Neon TLS am Proxy terminiert und der Backend-Prozess die
  Verbindung unverschlüsselt sieht. Kein Sicherheitsfinding.
- ✅ **Antwortzeiten unkritisch.** Die Queries liegen bei 18–53 ms (vorher lokale Datei, also
  praktisch 0 ms). Für zwei Endpunkte ohne Auto-Refresh ist das nicht spürbar; die
  Statusberechnung bleibt ohnehin serverseitig und in-memory.
- ⚠️ **Änderungswunsch (wichtigster Punkt) – fehlende `DATABASE_URL` reißt die Testsuite mit
  und meldet nur `KeyError`.** `app/db.py:10` liest die Variable per `os.environ[...]` auf
  Modulebene. `tests/test_api.py:10` importiert `app.db` (für `Base` und `get_db`), obwohl die
  Tests eine eigene In-Memory-SQLite-Engine benutzen und die PostgreSQL-Verbindung nie
  brauchen. Verifiziert (Variable entfernt, `load_dotenv` neutralisiert):
  `ERROR tests/test_api.py - KeyError: 'DATABASE_URL'`, Abbruch bereits beim Collect. Ohne
  `.env` ist also nicht nur der Start, sondern auch `python -m pytest` blockiert – und die
  Meldung nennt weder `.env` noch die nötige Variable. Empfehlung (kein Blocker): in `db.py`
  per `os.getenv` prüfen und mit einer klaren Meldung abbrechen („`DATABASE_URL` fehlt – `.env`
  anlegen, siehe CLAUDE.md"). Ein stiller SQLite-Default wäre die schlechtere Lösung: er würde
  eine Fehlkonfiguration im Betrieb verdecken.
- ⚠️ **Änderungswunsch – `create_all` bei jedem App-Start geht jetzt über das Netz.**
  `init_db()` im Lifespan war bei einer lokalen Datei gratis; jetzt braucht jeder Start eine
  erreichbare Datenbank (gemessen 0,39 s kalt) und die Anwendungsrolle DDL-Rechte. Für den
  Kurskontext in Ordnung und in `architecture.md` so dokumentiert. Sobald es Richtung Betrieb
  geht, gehört das Anlegen des Schemas in das Seed-Skript bzw. zu Migrationen, nicht in den
  App-Start.
- ⚠️ **Risiko (nicht reproduziert) – kein `pool_pre_ping`.** `create_engine(DATABASE_URL)`
  (`app/db.py:15`) nutzt den Default-Pool ohne Liveness-Check. Neon fährt die Compute-Instanz
  nach Leerlauf herunter; SQLAlchemy kann danach eine abgestandene Verbindung aus dem Pool
  ziehen, was den ersten Request nach einer Pause mit einem Verbindungsfehler scheitern lässt.
  Im Review nicht reproduziert – dazu müsste die Instanz erst lange genug idlen –, aber es ist
  die typische Stolperstelle bei serverlosem PostgreSQL. Absicherung ist eine Zeile:
  `create_engine(DATABASE_URL, pool_pre_ping=True)`.
- ⚠️ **Verhaltensunterschied zu SQLite – ID-Sequenzen laufen beim Neu-Seeden weiter.**
  `app/seed.py:55-57` löscht per `DELETE`; in PostgreSQL setzt das die `SERIAL`-Sequenz nicht
  zurück. Live sichtbar: `acts` hat 14 Zeilen bei `max(id) = 15`, `stages` 3 Zeilen bei
  `max(id) = 4`. Unter SQLite begannen die IDs nach dem Löschen wieder bei 1. Das
  Akzeptanzkriterium von US-1 („Erneutes Ausführen ersetzt die Daten, keine Duplikate") ist
  weiterhin erfüllt, und die IDs sind rein technisch (das Frontend nutzt sie nicht) – es ist
  also kosmetisch. Wer stabile IDs erwartet (z. B. in einer Demo oder einem späteren Test auf
  `id == 1`), stolpert hier. Falls gewünscht: `TRUNCATE ... RESTART IDENTITY` statt `DELETE`.
- ⚠️ **Testlücke – die neue `CheckConstraint` ist nicht getestet.** T-12 ist die einzige
  fachlich wirksame Änderung des Commits und durch keinen Test abgedeckt. Sie lässt sich im
  bestehenden Setup prüfen: verifiziert, dass auch SQLite CHECK-Constraints durchsetzt – ein
  `Act` mit `ends_at < starts_at` scheitert dort mit `IntegrityError`. Ein kleiner Test (in
  `tests/test_api.py` oder einem neuen `tests/test_models.py`) würde die Invariante festnageln,
  ohne Neon zu berühren.
- ⚠️ **Bekannte Grenze der Teststrategie.** Die Tests laufen bewusst gegen In-Memory-SQLite
  (kein Netz, keine Daten in Neon). Der Preis ist, dass genau die migrierte Schicht ungetestet
  bleibt: URL-Normalisierung, psycopg-Verbindung und PostgreSQL-spezifisches Verhalten. Das ist
  für dieses Projekt eine vertretbare Entscheidung, sollte aber bewusst so getragen werden – ein
  Fehler in `db.py:12-13` fällt erst beim manuellen Start auf, nicht in der Suite.
- ⚠️ **Weiterhin offen aus den Abschnitten 2 und 6** (unverändert durch diese Migration):
  TODO in `app/routers.py:15` (T-15), Test-Overrides auf Modulebene in `tests/test_api.py:36,39`
  (T-16), CWD-relativer `StaticFiles`-Pfad (T-17), `name`-Invarianten ohne `CheckConstraint`
  (T-18), doppelte Leerzeile in `app/crud.py`.
- ⚠️ **Kosmetisch.** `requirements.txt` endet ohne Zeilenumbruch und pinnt keine Versionen
  (unverändert zu v0.1, bei einer gehosteten DB aber etwas relevanter). `.gitignore` schließt
  weiterhin `*.db`/`*.sqlite*` aus – harmlos, da die Tests nur In-Memory arbeiten.

Keine ❌-Blocker gefunden.

### Nicht offensichtlich, fürs Protokoll

`load_dotenv()` ohne Argument sucht `.env` **datei-relativ**: python-dotenv läuft vom Frame des
Aufrufers (`app/db.py`) aus die Verzeichnisse nach oben. Der Start aus einem fremden
Arbeitsverzeichnis findet die `.env` also weiterhin – anders als der CWD-relative
`StaticFiles`-Pfad (T-17). Ausnahme: im REPL, unter einem Debugger (`sys.gettrace()` gesetzt)
oder bei `python -c` fällt python-dotenv auf das aktuelle Arbeitsverzeichnis zurück; dann wird
die `.env` nur gefunden, wenn dieses der Projektordner ist. Beim Debuggen aus einem anderen
Verzeichnis äußert sich das als `KeyError: 'DATABASE_URL'`.

### Gesamturteil (Nachtrag Phase 2)

**Freigeben mit (nicht blockierenden) Änderungswünschen.**

Die Umstellung ist sauber begrenzt: drei Dateien, keine Änderung an Modellen, API-Vertrag oder
Frontend, und die beiden fehleranfälligen Punkte einer solchen Migration – Zeitzonen-Semantik
und der Treiberwechsel – sind korrekt gelöst und live verifiziert. B2 und T1 in der neuen
Fassung sind erfüllt, Zugangsdaten liegen nicht in der Git-History. Die Testsuite ist grün,
deckt die migrierte Schicht aber nicht ab.

Der wichtigste Änderungswunsch ist die harte `KeyError`-Kopplung an `DATABASE_URL`, die ohne
`.env` auch das Testen blockiert; danach kommen `pool_pre_ping` als Absicherung gegen Neons
Idle-Suspend und ein Test für die neue `CheckConstraint`. Alle drei sind kleine, lokale
Änderungen und im Backlog als T-19 bis T-21 festgehalten. Keine Blocker; T-14 ist mit diesem
Nachtrag erledigt.

### Nachtrag zum Nachtrag – Umsetzung von T-19 bis T-21, Stand 2026-09-18

Die drei Änderungswünsche des Gesamturteils sind unmittelbar nach diesem Review umgesetzt und
verifiziert worden:

- **T-19 erledigt.** `app/db.py:10-17` liest die Variable per `os.getenv` und bricht sonst mit
  einem `RuntimeError` ab, der `.env`, das erwartete URL-Format und die Fundstelle in
  `CLAUDE.md` nennt. Verifiziert (Variable entfernt, `load_dotenv` neutralisiert): Import und
  `python -m pytest` melden jetzt genau diesen Text statt `KeyError: 'DATABASE_URL'`. Ein
  stiller SQLite-Fallback wurde bewusst nicht eingebaut – er würde eine Fehlkonfiguration im
  Betrieb verdecken. Die Tests brauchen damit weiterhin eine gesetzte `DATABASE_URL`
  (unverändert, aber jetzt selbsterklärend); eine echte Entkopplung würde `Base` aus `db.py`
  herauslösen und ist für den aktuellen Bedarf zu viel Struktur.
- **T-20 erledigt.** `app/db.py:26` erzeugt die Engine mit `pool_pre_ping=True`; der Kommentar
  nennt Neons Idle-Suspend als Grund. Live verifiziert: `engine.pool._pre_ping is True`, die
  Query-Zeiten bleiben unverändert bei 21–43 ms (der Check kostet nur beim Entnehmen einer
  gepoolten Verbindung).
- **T-21 erledigt.** Neu: `tests/test_models.py` mit drei Fällen – Ende nach Start wird
  angenommen, Ende vor Start und Ende gleich Start scheitern mit `IntegrityError`. Damit ist
  die Grenze `>` statt `>=` mitgeprüft. Eigene Engine pro Test über eine Fixture, kein
  `TestClient`, keine Modulebene-Overrides (also nicht betroffen von T-16).

Suite nach den Änderungen: **18 passed** (vorher 15), keine neuen Warnungen. Die ⚠️-Punkte
T-15 bis T-18 bleiben unverändert offen.

## 8. Nachtrag – v0.3: US-7 (Tailwind, responsive) und US-8 (Tage gruppieren/filtern), Stand 2026-09-21

Review des Commits `fa7a0f6` (Code-Anteil: `app/crud.py`, `app/routers.py`, `app/schedule.py`,
`app/seed.py`, `static/index.html`, `static/app.js`, `static/style.css`, `tailwind/input.css`,
`tests/test_api.py`, `tests/test_schedule.py`, `.gitignore`) gegen die Akzeptanzkriterien in
`doc/backlog.md`, `doc/requirements.md` (C6, C10, F4, F6, F9, B4, B6, T1), `doc/architecture.md`
und `CLAUDE.md`.

Verifikation:

- `python -m pytest -q`: **27 passed** (vorher 18; neu sind 6 API-Tests und 3 Unit-Tests),
  dieselben 2 bekannten Deprecation-Warnings.
- `static/style.css` mit dem Tailwind-CLI-Binary (v4.3.3) neu erzeugt: **byte-identisch** zur
  eingecheckten Datei. Das eingecheckte CSS ist also aktuell, und alle in `app.js` gesetzten
  Klassen (u. a. `sm:grid-cols-[7rem_1fr_10rem]`, `border-l-green-600`, `min-h-11`) sind
  enthalten.
- App lokal gegen eine **Wegwerf-SQLite-DB** gestartet (nicht gegen Neon, damit die Daten dort
  unverändert bleiben), per `python -m app.seed` befüllt, API per `curl` geprüft und die
  Oberfläche mit Headless-Chrome bei 360 px und 1280 px gerendert.

### Erfüllung der Akzeptanzkriterien US-7

- **Tailwind statt eigenem CSS – erfüllt.** Das handgeschriebene CSS ist vollständig ersetzt;
  `tailwind/input.css` enthält nur Import und `@source`.
- **CSS-Build mit der Tailwind-CLI, dokumentiert – erfüllt.** Befehle stehen in `CLAUDE.md`
  unter „Build CSS"; das Binary ist über `.gitignore` ausgeschlossen.
- **Kein JS-Framework, kein JS-Build (F4) – erfüllt.** `app.js` ist unverändert Vanilla JS und
  wird direkt ausgeliefert.
- **360 px ohne horizontales Scrollen, Desktop übersichtlich – erfüllt.** Bei 360 px sind Zeit,
  Titel und Bühne in einer Zeile lesbar, die beiden Filter stehen nebeneinander im
  2-Spalten-Raster. Ab `sm` wird der Eintrag zum Raster `7rem | 1fr | 10rem`, der Inhalt ist
  auf `max-w-3xl` zentriert.
- **Touch-Bedienbarkeit – erfüllt.** Beide Auswahlfelder haben `min-h-11` (44 px, gängige
  Mindestgröße für Touch-Ziele) und `text-base` (verhindert Auto-Zoom unter iOS).
- **Funktionen unverändert, „läuft jetzt"/„als Nächstes" unterscheidbar – erfüllt,** grün
  bzw. bernsteinfarben mit farbigem linkem Rand. Siehe aber den ⚠️-Punkt zur fehlenden
  Beschriftung.
- **Entscheidung CSS einchecken und Herkunft der CLI – erfüllt,** in `CLAUDE.md`
  („Project Decisions") und im Backlog dokumentiert.

### Erfüllung der Akzeptanzkriterien US-8

- **Seed über mindestens zwei Tage ab heute – erfüllt.** Es sind vier Tage mit 14/10/12/8 Acts,
  darunter zwei Acts über Mitternacht („Night Owls" 23:00–01:00, „Afterhour Collective"
  22:30–02:00). `/api/days` liefert live die vier Tage ab 2026-09-21.
- **Gruppierung mit Überschrift „Fr, 18.09." – erfüllt.** `formatDay()` berechnet den Wochentag
  per `Date.UTC`/`getUTCDay`, also unabhängig von Zeitzone und Sprache des Geräts. Das ist gut
  gelöst, weil ein `new Date("2026-09-21")` in westlichen Zeitzonen auf den Vortag kippen würde.
- **Tages-Auswahl „Alle Tage" + Tage mit Acts, chronologisch – erfüllt.**
- **Act gehört zum Starttag – erfüllt und getestet**, sowohl im Backend
  (`festival_day`, `test_act_past_midnight_belongs_to_its_start_day`,
  `test_days_are_sorted_and_use_the_start_day`) als auch im Frontend
  (`starts_at.slice(0, 10)`).
- **Tages- und Bühnenfilter kombinierbar, Status nach dem Filter – erfüllt und getestet**
  (`test_program_filtered_by_day_and_stage`, `test_status_is_computed_within_the_selected_day`).
- **`GET /api/program?day=` und `GET /api/days` – erfüllt.** Ein Tag ohne Acts liefert `[]`,
  ein ungültiges Datum `422` (FastAPI validiert `date`), eine leere DB liefert `[]` für `/api/days`.
  Der Tagesfilter ist ein Bereichsfilter `[Tag 00:00, Folgetag 00:00)` statt eines
  `date()`-Casts und verhält sich so unter SQLite und PostgreSQL gleich.
- **Eintägiges Festival übersichtlich – erfüllt** (eine Gruppe, ein Eintrag in der Auswahl;
  per Code-Durchsicht geprüft, nicht live).
- **Tagesfilter und Überschriften auf 360 px bedienbar/lesbar – erfüllt** (siehe US-7).

### Findings

- ⚠️ **UX – Status nur über Farbe, ohne Beschriftung.** „Läuft jetzt" und „als Nächstes" sind
  nur durch Hintergrund- und Randfarbe erkennbar; es gibt weder Text noch Legende. Wer die Farben
  nicht kennt oder Grün und Bernstein schlecht unterscheiden kann, erkennt den Status nicht
  „sofort" (C2). Das war schon in v0.1 so, ist also keine Regression. Durch US-8 wird es aber
  wichtiger: Bei Auswahl eines späteren Tages ist dessen erster Act „als Nächstes" markiert
  (bewusste, dokumentierte Folge von „Status nach dem Filter"), obwohl heute noch Acts kommen.
  Ohne Beschriftung ist dieser Unterschied nicht erklärbar. Vorschlag: ein kleines Text-Badge
  („läuft jetzt" / „als Nächstes") im Eintrag, die Klassen dabei vollständig ausgeschrieben.
- ⚠️ **Race Condition bei schnellem Filterwechsel.** `loadProgram()` (`static/app.js:25`) startet
  bei jeder Änderung einen neuen `fetch`, ohne ältere Anfragen abzubrechen. Kommen die Antworten
  in anderer Reihenfolge zurück als abgeschickt (z. B. bei schlechtem Empfang auf dem Gelände oder
  bei Neons Kaltstart), zeigt die Liste das Ergebnis der *vorletzten* Auswahl, obwohl die
  Dropdowns die letzte anzeigen. Mit zwei Filtern ist das wahrscheinlicher als in v0.1. Abhilfe
  ohne neue Dependency: `AbortController` oder ein Anfragezähler, der veraltete Antworten
  verwirft.
- ⚠️ **Irreführender Leer-Hinweis bei Filterkombinationen.** Liefert eine Kombination aus Tag und
  Bühne keine Acts, erscheint „Es sind noch keine Programmpunkte vorhanden." – das klingt nach
  leerer Datenbank, nicht nach leerer Auswahl. Mit den Seed-Daten tritt das nicht auf, weil jede
  Bühne an jedem Tag bespielt wird, bei echten Daten aber schon. Vorschlag: Text abhängig davon,
  ob ein Filter gesetzt ist (z. B. „Für diese Auswahl gibt es keine Acts.").
- ⚠️ **Testlücke – Seed-Logik über Mitternacht.** `build_acts()` (`app/seed.py`) schiebt `ends_at`
  um einen Tag weiter, wenn das Ende vor dem Start liegt. Genau diese Stelle erzeugt die Daten, an
  denen US-8 geprüft wird, ist aber nicht getestet. `build_acts()` ist ohne DB aufrufbar, ein Test
  wäre also klein: Anzahl der Tage, `ends_at > starts_at` für alle Acts, „Night Owls" endet am
  Folgetag. Randnotiz: Ein Slot mit identischer Start- und Endzeit würde wegen `<=` stillschweigend
  zu einem 24-Stunden-Act statt an der `CheckConstraint` zu scheitern. Bei den festen Seed-Daten
  ist das nur theoretisch.
- ⚠️ **Doku – `requirements.md` ist an zwei Stellen veraltet.** Die Statuszeile sagt „neue
  Anforderungen aufgenommen, noch nicht umgesetzt", und der Absatz „Erweiterbarkeit (Leitplanke,
  keine Umsetzung in der aktuellen Version)" nennt den Tagesfilter (F6) noch als zukünftig. Beides
  stimmt seit US-7/US-8 nicht mehr (C6, C10, F6, F9 und der Tages-Teil von B6 sind umgesetzt).
  `backlog.md`, `architecture.md`, `project-status.md` und `CLAUDE.md` sind dagegen aktuell.
- ✅ **Architektur-Regeln eingehalten.** Die Queries liegen in `crud.py`, die Tagesregel als reine
  Funktionen in `schedule.py` mit Unit-Tests, der Endpunkt bleibt dünn und der API-Vertrag
  wurde nur um den optionalen Parameter `day` erweitert. Es gibt keine neue Python-Dependency und
  keine neue Datei außer `tailwind/input.css`. Nebenbei behoben: die doppelte Leerzeile in
  `app/crud.py` aus Abschnitt 7.
- ⚠️ **Weiterhin offen** (unverändert durch US-7/US-8): T-15 bis T-18.

Keine ❌-Blocker gefunden.

### Nicht offensichtlich, fürs Protokoll

- Die Tagesregel steht bewusst an zwei Stellen, in `schedule.festival_day()` und in
  `groupByDay()` (`app.js`). Beide dürfen nur deshalb einfach das Datum aus `starts_at` nehmen,
  weil Zeitstempel naiv in Festival-Ortszeit gespeichert und ausgeliefert werden. Wer das je auf
  UTC oder zeitzonenbehaftete Zeitstempel umstellt, muss beide Stellen anpassen, sonst landen
  Acts nach 22:00 in der Gruppe des Folgetags.
- `list_days()` lädt alle unterschiedlichen `starts_at` und bildet die Tage in Python statt per
  SQL-`DISTINCT date(...)`. Das ist dieselbe Begründung wie beim Bereichsfilter (gleiches
  Verhalten unter SQLite und PostgreSQL) und bei ein paar Dutzend Acts unerheblich.
- `@source "../static"` lässt Tailwind auch die eigene Ausgabe `static/style.css` scannen.
  Nachgeprüft ist das harmlos: Ein Build, der nur `*.html`/`*.js` scannt, ist byte-identisch.
- Headless-Chrome hat eine Mindest-Fensterbreite. Ein Screenshot mit `--window-size=360,…`
  sieht daher abgeschnitten aus, obwohl die Seite korrekt ist. Für den 360-px-Check wurde die
  Seite in einem 360 px breiten `iframe` gerendert.

### Gesamturteil (Nachtrag v0.3)

**Freigeben mit (nicht blockierenden) Änderungswünschen.**

Alle Akzeptanzkriterien von US-7 und US-8 sind erfüllt. Die fachlich heikle Regel „Act gehört zum
Starttag" ist in Backend und Frontend konsistent umgesetzt und im Backend getestet. Das
eingecheckte CSS stimmt mit einem frischen Build überein, und die Oberfläche funktioniert bei
360 px wie am Desktop. Die Änderungswünsche betreffen die Bedienung (Status-Beschriftung,
Race Condition, Leer-Hinweis), eine Testlücke im Seed und veraltete Stellen in
`requirements.md`. Sie sind im Backlog als T-22 bis T-26 festgehalten.

**Nachtrag 2026-09-21:** T-26 ist erledigt. In `requirements.md` sind die Statuszeile und der
Absatz „Erweiterbarkeit" an den umgesetzten Stand angepasst.

**Nachtrag 2026-09-21 (2):** T-22 und T-23 sind erledigt. Neben der Farbe markiert jetzt ein
Text-Badge („läuft jetzt" / „als Nächstes") den Status, und ein Anfragezähler in
`loadProgram()` verwirft veraltete Antworten. T-23 wurde mit einem verzögerten Mock-`fetch`
nachgestellt (langsame Antwort für Bühne A, schnelle für Bühne B, A vor B gewählt): Vorher
zeigte die Liste A, jetzt zeigt sie B.

**Nachtrag 2026-09-21 (3):** T-24 und T-25 sind erledigt, damit sind alle Änderungswünsche aus
diesem Abschnitt umgesetzt. Mit gesetztem Filter lautet der Leer-Hinweis jetzt „Für diese Auswahl
gibt es keine Acts.". `tests/test_seed.py` deckt `build_acts()` ab; ohne die
Mitternachts-Korrektur schlagen 2 der 5 Tests fehl. `python -m pytest`: 32 passed.

**Nachtrag 2026-09-21 (4):** Auch die älteren Punkte T-15 bis T-18 aus Abschnitt 6 sind
erledigt. T-15: TODO entfernt, die Antwortmodelle bleiben in `routers.py`. T-16: Overrides in
einer Fixture mit Teardown. T-17: `STATIC_DIR` relativ zu `main.py`, Start aus einem fremden
Ordner geprüft. T-18: `CheckConstraint`s für nicht leere Namen. Neu und nicht im Review
vorgesehen: `seed.py` legt die Tabellen neu an (`drop_all` + `create_all`), weil `create_all`
bestehende Tabellen nicht ändert und die Constraints sonst nie in Neon ankämen. Das löst
nebenbei den Hinweis zu den weiterlaufenden ID-Sequenzen aus Abschnitt 7. `python -m pytest`:
36 passed. Aus den Abschnitten 6 bis 8 ist damit nichts mehr offen.
