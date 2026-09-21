# Architektur & Projektstruktur

Status: laufend, Stand 2026-09-18. Phase 1 (v0.2) hat die ursprüngliche Ein-Datei-Struktur
(`db.py` mit Modell + Queries direkt in `main.py`) abgelöst; die Struktur wächst seitdem
schrittweise mit den Anforderungen weiter, statt auf einem MVP-Stand zu verharren. Phase 2
(v0.2) hat die Datenhaltung von SQLite auf PostgreSQL (Neon) umgestellt – ohne Änderung an
Modellen, API-Vertrag oder Frontend.

Grundlage: [`requirements.md`](requirements.md), [`domain-model.md`](domain-model.md) und die
Entscheidungen in [`../CLAUDE.md`](../CLAUDE.md) (Festival-Zeitzone UTC+02:00, pytest + httpx
als Dev-Dependencies).

Leitlinie: nicht mehr „so klein wie möglich" (MVP), sondern gut strukturiert und erweiterbar –
die Struktur nimmt Schritt für Schritt an Komplexität zu, sobald das Projekt es verlangt. Mit
drei Entitäten (`Artist`, `Stage`, `Act`) und Joins reicht eine einzige Datei für Modell +
Queries + Endpunkte nicht mehr aus – deshalb kommen `models.py`, `crud.py` und `routers.py`
dazu. Jede weitere Schicht (Datei, Paket, Klasse) wird eingeführt, sobald sie einen konkreten
Bedarf löst – nicht spekulativ auf Vorrat, aber auch nicht mehr aus Prinzip vermieden. Siehe
„Erweiterungspunkte" für absehbare nächste Schritte.

## Projektstruktur

```text
festival-planner/
├── app/
│   ├── __init__.py        leer – macht app/ zum importierbaren Paket
│   ├── main.py            FastAPI-App: Objekt, Lifespan (init_db), bindet routers.py + static/ ein
│   ├── models.py          ORM-Modelle: Artist, Stage, Act (siehe domain-model.md)
│   ├── db.py              Datenbank-Infrastruktur: DATABASE_URL aus .env, Engine, Session, init_db(), get_db()
│   ├── crud.py            Queries: Bühnenliste, Tagesliste, Programmliste (Joins über Artist/Stage)
│   ├── routers.py         API-Endpunkte: GET /api/program, GET /api/stages, GET /api/days
│   ├── schedule.py        Business-Logik: Festival-Zeit, Festivaltag, „läuft jetzt" / „als Nächstes"
│   └── seed.py            Seed-Skript: Tabellen neu anlegen, Artists/Stages und Acts einfügen
├── static/
│   ├── index.html         die einzige Seite
│   ├── style.css          von der Tailwind-CLI erzeugt (eingecheckt, nicht von Hand ändern)
│   └── app.js             API abrufen, Liste rendern, Tages-/Bühnenfilter, Status-Badges, Favoriten
├── tailwind/
│   └── input.css          Tailwind-Quelle für static/style.css
├── tests/
│   ├── test_schedule.py   Unit-Tests der Business-Logik (ohne DB, ohne HTTP)
│   ├── test_models.py     DB-seitige Invarianten der Modelle (In-Memory-SQLite)
│   ├── test_api.py        wenige API-Tests (TestClient + In-Memory-SQLite, nicht Neon)
│   └── test_seed.py       Seed-Daten aus build_acts() (ohne DB): Tage, Acts über Mitternacht
├── .env                   DATABASE_URL (nicht eingecheckt)
├── requirements.txt       Laufzeit: fastapi, uvicorn[standard], sqlalchemy, psycopg[binary], python-dotenv
└── requirements-dev.txt   -r requirements.txt + pytest + httpx
```

Die Programmdaten liegen in einer PostgreSQL-Datenbank bei Neon; es entsteht keine lokale
Datenbankdatei mehr. `.env` mit der `DATABASE_URL` ist per `.gitignore` von Git ausgeschlossen.

## Verantwortlichkeiten

| Datei | Verantwortung | Abhängig von |
|---|---|---|
| `app/models.py` | ORM-Modelle `Artist`, `Stage`, `Act` inkl. `relationship()` (siehe `domain-model.md`). | SQLAlchemy, `db.Base` |
| `app/db.py` | `DATABASE_URL` aus `.env` laden und auf den `psycopg`-Treiber normalisieren, Engine, Session-Factory, FastAPI-Dependency `get_db()`, `Base`, `init_db()` (Tabellen anlegen). Reine Infrastruktur, kein Modell mehr. | SQLAlchemy, `psycopg`, `python-dotenv` |
| `app/crud.py` | Queries als einfache Funktionen: Bühnenliste (sortiert), Tagesliste (Tage mit Acts, sortiert), Programmliste (`Act` mit Join auf `Artist`/`Stage`, sortiert, optional nach Bühne und Tag gefiltert). | `models`, `db` (Session), `schedule` (Tagesregel) |
| `app/routers.py` | Die drei API-Endpunkte, Pydantic-Antwortmodelle; ruft `crud.py` für die Daten und `schedule.py` für den Status auf. | `crud`, `schedule`, FastAPI |
| `app/schedule.py` | `FESTIVAL_TZ`, `festival_now()`, die Tagesregel (`festival_day()`, `day_bounds()`) und reine Funktion(en), die Acts anhand eines übergebenen Zeitpunkts einen Status zuordnen. | nur `datetime` – **kein** FastAPI, **keine** Session |
| `app/main.py` | App-Objekt, `init_db()` beim Start, bindet `routers.py` und `static/` ein. Enthält selbst keine Endpunkte mehr. | `db`, `routers` |
| `app/seed.py` | `python -m app.seed`: Tabellen löschen und neu anlegen, Artists und Stages anlegen, Acts für vier Festivaltage (ab heute) auf 3 Bühnen mit FK-Referenzen einfügen. | `db`, `models`, `schedule` |
| `static/*` | HTML + Vanilla JS, gestaltet mit Tailwind-Klassen; `style.css` ist erzeugt. Lädt Bühnen und Programm über die API, rendert die Liste, filtert per Dropdown, hebt Status hervor. | nur die HTTP-API |

## Wo liegt was?

| Bereich | Ort |
|---|---|
| API | `app/routers.py` |
| Datenbank-Infrastruktur | `app/db.py` |
| Modelle | `app/models.py` |
| Datenbank-Queries | `app/crud.py` (Joins über `Artist`/`Stage` – weiterhin nur Funktionen, keine Repository-Klassen) |
| Business-Logik | `app/schedule.py` |
| Frontend | `static/` |
| Tests | `tests/` |

Ablauf einer Anfrage:

```text
app.js ──GET /api/program?stage=X──▶ routers.py ──ruft auf──▶ crud.py ──select+join──▶ db.py (PostgreSQL/Neon)
                                          │
                                          └──items + now──▶ schedule.py ──status──▶ JSON
```

## HTTP-API

Ein Prozess (uvicorn) liefert API und Frontend aus (T2).

**API-Vertrag: flach statt verschachtelt (Entscheidung, T-4).** Obwohl `Act` selbst keine
`title`/`stage`-Felder mehr hat (siehe `domain-model.md`), liefert die API weiterhin flache
Strings – befüllt aus `act.artist.name` bzw. `act.stage.name`.

Verworfene Alternative – verschachtelte Objekte, die die neue Entitätstrennung 1:1 abbilden:

```json
{
  "id": 1,
  "artist": { "name": "Band A" },
  "stage": { "name": "Hauptbühne" },
  "starts_at": "2026-09-10T13:30:00",
  "ends_at": "2026-09-10T14:30:00",
  "status": "now"
}
```

Dagegen entschieden, weil:

* `static/app.js` erwartet `item.title` und `item.stage` als Strings; mit verschachtelten
  Objekten müsste das Frontend angepasst werden.
* Phase 1 hat als Ziel „Funktionalität erhalten, nur Datenbank-Struktur ändern" – ein
  Frontend-Umbau gehört nicht dazu und würde Scope und Risiko unnötig vergrößern.
* Der flache Vertrag ist für die aktuellen zwei Endpunkte ausreichend; eine spätere
  Erweiterung um zusätzliche Felder (z. B. Genre, Kapazität) ist auch mit flachen Strings
  möglich (siehe „Erweiterungspunkte" unten), ohne dass sich der Vertrag grundsätzlich
  ändern muss.

Der Preis dieser Entscheidung: `crud.py` muss die Umbenennung (`artist.name` → `title`,
`stage.name` → `stage`) explizit vornehmen – die Pydantic-Antwortmodelle in `routers.py`
bilden das ORM-Modell also nicht direkt ab.

### `GET /api/program?stage=<name>&day=<YYYY-MM-DD>`

Programmpunkte chronologisch nach `starts_at` sortiert, bei gleicher Startzeit alphabetisch
nach Bühnenname (`ORDER BY Act.starts_at, Stage.name` über den Join – feste Reihenfolge, auch
für Tests), optional nach Bühne (B1) und/oder Tag (B6, F6) gefiltert.
Eine unbekannte Bühne und ein Tag ohne Acts liefern eine leere Liste, keinen Fehler; ein
ungültiges Datum in `day` lehnt FastAPI mit 422 ab.
Der Tagesfilter nutzt die Tagesregel aus `schedule.py` (siehe „Festivaltage") und filtert per
Bereich `day 00:00 <= starts_at < day+1 00:00` statt per `date()`-Cast – das verhält sich auf
PostgreSQL und der In-Memory-SQLite der Tests gleich.

```json
{
  "now": "2026-09-10T14:05:00",
  "items": [
    {
      "id": 1,
      "title": "Band A",
      "stage": "Hauptbühne",
      "starts_at": "2026-09-10T13:30:00",
      "ends_at": "2026-09-10T14:30:00",
      "status": "now"
    }
  ]
}
```

`title` kommt aus `Artist.name`, `stage` aus `Stage.name` (Join in `crud.py`). `status` ist
`"now"`, `"next"` oder `null`. `now` ist die serverseitig bestimmte Festival-Zeit (T3), damit
das Frontend sie anzeigen kann.

### `GET /api/stages`

Alphabetisch sortierte Liste der Bühnennamen aus der `Stage`-Tabelle, für das Filter-Dropdown.

```json
["Hauptbühne", "Waldbühne", "Zeltbühne"]
```

### `GET /api/days`

Chronologisch sortierte Liste der Tage, an denen mindestens ein Act beginnt, für das
Tages-Dropdown (US-8). Abgeleitet aus `Act.starts_at` – es gibt keine eigene Tag-Entität.

```json
["2026-09-18", "2026-09-19"]
```

### `GET /`

Liefert `static/index.html`; `static/` wird per `StaticFiles` eingebunden. Der Pfad
(`STATIC_DIR`) wird relativ zu `app/main.py` aufgelöst, nicht zum Arbeitsverzeichnis – die App
startet also auch außerhalb des Projektordners (T-17).

## Business-Logik: „läuft jetzt" / „kommt als Nächstes"

Regeln für einen Zeitpunkt `now`:

- **now:** `starts_at <= now < ends_at`. Mehrere Treffer sind möglich (parallele Bühnen).
- **next:** alle Punkte, deren `starts_at` der früheste Startzeitpunkt nach `now` ist
  (bei gleicher Startzeit mehrere).
- sonst `null`.

Der Status wird **nach** dem Bühnen- und Tagesfilter berechnet. Dadurch ist „als Nächstes" auf
einer gefilterten Bühne automatisch korrekt (Benutzeraktion 4). Folge beim Tagesfilter: Wer
einen späteren Tag auswählt, sieht dessen ersten Act als „als Nächstes" markiert – bezogen auf
die angezeigte Liste ist das der nächste Act.

## Festivaltage

- Ein Act gehört zu dem Tag, an dem er **beginnt** (`festival_day(starts_at)`), auch wenn er
  nach Mitternacht endet (z. B. 23:00–01:00). Festgelegt in US-8.
- `day_bounds(day)` liefert `[day 00:00, day+1 00:00)` für den Filter in `crud.py`.
- Beides sind reine Funktionen in `schedule.py`, getestet in `tests/test_schedule.py`. Das
  Frontend gruppiert nach derselben Regel (Datum aus `starts_at`).

Die Funktionen bekommen `now` als Parameter – sie lesen die Uhr nicht selbst. Das macht sie
ohne Tricks testbar.

## Zeit und Zeitzone

- `FESTIVAL_TZ` ist der feste Offset UTC+02:00 (Entscheidung in `CLAUDE.md`).
- Zeitstempel werden **naiv in Festival-Ortszeit** gespeichert (ohne Zeitzonen-Info).
  Die Spalten sind `DateTime` ohne `timezone=True`, in PostgreSQL also
  `timestamp without time zone`; damit bleiben die Seed-Daten lesbar und es gibt keine
  implizite Umrechnung.
- `festival_now()` liefert passend dazu die aktuelle Zeit in UTC+02:00, ebenfalls naiv.
- In `routers.py` wird `festival_now` als FastAPI-Dependency verwendet. Tests ersetzen sie über
  `app.dependency_overrides` durch einen festen Zeitpunkt.

## Datenbank

- **PostgreSQL, gehostet bei Neon** (seit v0.2 Phase 2, vorher eine lokale SQLite-Datei).
  Treiber ist `psycopg` (v3).
- Die Verbindung kommt aus `DATABASE_URL` in `.env` und wird in `db.py` per `python-dotenv`
  geladen – nicht im Code verdrahtet (B2). `.env` ist nicht eingecheckt.
- Fehlt die Variable, bricht `db.py` beim Import mit einem `RuntimeError` ab, der `.env` und
  das erwartete Format nennt. Bewusst **kein** stiller SQLite-Fallback: der würde eine
  Fehlkonfiguration im Betrieb verdecken.
- `pool_pre_ping=True` an der Engine: Neon fährt die Compute-Instanz im Leerlauf herunter, und
  im Pool bleiben dann tote Verbindungen liegen. Ohne den Check scheitert der erste Request
  nach einer Pause; mit ihm verwirft SQLAlchemy die Verbindung und baut eine neue auf.
- Nicht offensichtlich: `load_dotenv()` sucht die `.env` **datei-relativ** (aufwärts ab
  `app/db.py`), nicht im Arbeitsverzeichnis – der Start aus einem anderen Ordner funktioniert
  also. Ausnahme: im REPL, unter einem Debugger oder bei `python -c` fällt python-dotenv auf
  das aktuelle Arbeitsverzeichnis zurück; dann wird die `.env` nur dort gefunden.
- Nicht offensichtlich: Eine `postgresql://`-URL wird in `db.py` auf `postgresql+psycopg://`
  normalisiert. SQLAlchemy erwartet bei der kurzen Form sonst `psycopg2`, das nicht
  installiert ist.
- Drei Tabellen für `Artist`, `Stage`, `Act` (siehe `domain-model.md`), angelegt per
  `Base.metadata.create_all` in `init_db()` – beim App-Start und im Seed-Skript.
- Datenintegrität: `ends_at > starts_at` ist als `CheckConstraint` auf `Act` DB-seitig
  erzwungen, nicht nur in der Business-Logik; ebenso `trim(name) <> ''` auf `Artist` und
  `Stage` (T-18).
- Keine Migrationen: Bei Schemaänderungen wird neu geseedet. Nicht offensichtlich:
  `create_all` legt nur fehlende Tabellen an und ändert bestehende nie. Deshalb löscht
  `seed.py` die Tabellen (`drop_all`) und legt sie neu an – nur so kommen z. B. neue
  Constraints in einer bestehenden Neon-Datenbank an. Nebeneffekt: Die IDs beginnen wieder
  bei 1.
- `connect_args={"check_same_thread": False}` ist mit dem Wechsel weggefallen – das war eine
  reine SQLite-Eigenheit. In `tests/test_api.py` steht es weiterhin, weil die Tests eine
  In-Memory-SQLite-DB verwenden.

## Seed-Daten

Das Seed-Skript legt das Festival auf **vier Tage ab dem heutigen Datum** (in Festival-Zeit),
je ein Slot-Block pro Tag (`FESTIVAL_DAYS` in `seed.py`). So läuft in einer Demo tatsächlich
gerade etwas, ohne dass eine Funktion zum Simulieren der Uhrzeit nötig ist, und Tagesfilter und
Gruppierung sind prüfbar. Je ein Act am zweiten und dritten Tag (23:00–01:00, 22:30–02:00) endet nach Mitternacht: Liegt
die Endzeit eines Slots vor der Startzeit, setzt das Skript das Ende auf den Folgetag.
Reihenfolge beim Einfügen: erst `Artist`- und `Stage`-Zeilen, danach `Act`-Zeilen mit den
passenden FK-Referenzen.

## Frontend

- Beim Laden: `GET /api/stages` und `GET /api/days` für die beiden Dropdowns, dann
  `GET /api/program`.
- Bei Filterwechsel (Tag oder Bühne): erneut `GET /api/program?stage=…&day=…` mit beiden
  aktuellen Werten. Nicht offensichtlich: Bei schnellem Wechsel können die Antworten in anderer
  Reihenfolge ankommen, als sie abgeschickt wurden. Ein Anfragezähler (`latestProgramRequest`)
  sorgt dafür, dass nur die Antwort auf die jüngste Anfrage gerendert wird (T-23).
- Anzeige: nach Tag gruppiert – pro Tag eine Überschrift („Fr, 18.09.") und eine Liste. Der
  Wochentag wird von Hand aus dem Datum berechnet (nicht über `Intl`/Geräte-Locale).
  Pro Eintrag Uhrzeit (HH:MM), Titel, Bühne; `status` bestimmt die Tailwind-Klassen des
  Eintrags (farbiger linker Rand + Hintergrund, `STATUS_CLASSES` in `app.js`) und zusätzlich
  ein Text-Badge „läuft jetzt" / „als Nächstes" hinter dem Titel (`STATUS_BADGES`), damit der
  Status nicht nur über die Farbe erkennbar ist (T-22).
- Gestaltung mit Tailwind CSS (F9): Mobil (ab 360 px) untereinander umbrechend, ab `sm`
  (640 px) als Raster Zeit | Titel | Bühne | Stern, Inhalt auf `max-w-3xl` begrenzt.
- CSS-Build: `tailwind/input.css` → `static/style.css` über die Tailwind-CLI (Standalone-Binary,
  kein Node/npm). Nicht offensichtlich: Tailwind erzeugt nur Klassen, die es als vollständige
  Strings in `static/` findet – dynamisch zusammengesetzte Klassennamen fehlen im CSS.
  Die erzeugte Datei ist eingecheckt, damit der Betrieb keinen Build-Schritt braucht (T2).
  Befehle: [`../CLAUDE.md`](../CLAUDE.md#build-css-nur-bei-änderungen-am-frontend).
- Leere Liste: Ohne Filter lautet der Hinweis „Es sind noch keine Programmpunkte vorhanden.",
  mit gesetztem Tages- oder Bühnenfilter „Für diese Auswahl gibt es keine Acts." (T-24).
- Favoriten (US-9): Stern-Button pro Eintrag (☆/★, `aria-pressed`). Gespeichert wird nur im
  Browser, als JSON-Array von Act-`id`s im `localStorage` (Schlüssel
  `festival-planner.favorites`) – keine Übertragung an den Server, kein Backend-Anteil.
  Lesen und Schreiben stehen in `try/catch`: Ohne verfügbaren Speicher (privater Modus,
  blockierte Website-Daten) gelten die Favoriten nur bis zum Neuladen. Die `id` als Kennung
  reicht, solange die Daten nur per Seed entstehen (deterministisch, Tabellen werden neu
  angelegt); mit einem Import (B7) ist das neu zu bewerten.
- Persönlicher Zeitplan (US-10): Bereich „Meine Favoriten" über dem Programm, immer mit allen
  Favoriten (Tag, Uhrzeit, Titel, Bühne), unabhängig vom Filter. Dafür lädt `app.js` beim
  Seitenaufruf einmal zusätzlich `GET /api/program` ohne Filter und filtert clientseitig auf
  die Favoriten-`id`s; die gefilterte Programmliste lässt sich dafür nicht nutzen. Kein neuer
  Endpunkt. Unbekannte `id`s fallen dabei stillschweigend weg. Ein Stern-Klick rendert den
  Bereich sofort neu. Die Liste ist auf `max-h-60` begrenzt und scrollt intern, damit viele
  Favoriten das Programm nicht weit nach unten schieben. Der Bereich ist ein natives
  `<details>`-Akkordeon, beim Laden zugeklappt; die Kopfzeile zeigt die Anzahl. Nicht
  offensichtlich: `display: flex` am `<summary>` blendet den nativen Pfeil aus, deshalb steht
  ein eigener Pfeil im Markup, der sich per `group-open:rotate-90` dreht.
- Mobil steht die Bühne in einer eigenen Zeile unter Zeit, Titel und Stern (`order-last
  basis-full`), ab `sm` wieder im Raster Zeit | Titel | Bühne | Stern.
- Aktualisierung durch Neuladen der Seite – keine Echtzeit-Updates (Scope-Abgrenzung).

## Tests

Start mit `python -m pytest` im Projektordner. Durch `python -m` liegt das Projektverzeichnis
im Importpfad – daher keine `conftest.py` und keine `pytest.ini` nötig.

- `tests/test_schedule.py` – der Schwerpunkt: Statusregeln inkl. Randfällen (genau
  Start-/Endzeitpunkt, parallele Acts, gleiche Startzeiten, nichts mehr kommt, gefilterte Liste).
- `tests/test_models.py` – die DB-seitige Invariante `ends_at > starts_at` (`CheckConstraint`):
  Ende nach Start wird angenommen, Ende vor Start und Ende gleich Start werden mit
  `IntegrityError` abgelehnt. Außerdem leere oder nur aus Leerzeichen bestehende Namen bei
  `Artist` und `Stage`. Eigene Engine pro Test (Fixture), kein `TestClient`. Läuft unter
  In-Memory-SQLite, weil SQLite CHECK-Constraints ebenfalls durchsetzt.
- `tests/test_seed.py` – die Seed-Daten aus `build_acts()`, ohne DB: ein Act pro Slot, vier
  aufeinanderfolgende Tage ab dem Starttag, `ends_at > starts_at` für alle Acts, ein Act über
  Mitternacht („Night Owls") endet am Folgetag und gehört zu seinem Starttag, eine `Stage` pro
  Bühnenname (sonst scheitert die Unique-Constraint). Wichtig, weil US-8 an genau diesen Daten
  im Browser geprüft wird.
- `tests/test_api.py` – wenige Tests: Sortierung, Bühnen- und Tagesfilter (auch kombiniert),
  Bühnen- und Tagesliste, `status` im JSON (auch innerhalb eines gewählten Tages).
  Nutzt In-Memory-SQLite – bewusst **nicht** die PostgreSQL-Datenbank: die Tests laufen so
  ohne Netzwerk und hinterlassen keine Daten in Neon. Der Preis: die migrierte
  Infrastrukturschicht (URL-Normalisierung, psycopg-Verbindung, PostgreSQL-spezifisches
  Verhalten) wird dadurch nicht abgedeckt. Ersetzt `get_db` und `festival_now` per
  `dependency_overrides` – in einer autouse-Fixture, die sie nach jedem Test wieder entfernt,
  damit sie nicht in andere Testmodule durchschlagen (T-16).
  Nicht offensichtlich: Eine gesetzte `DATABASE_URL` brauchen die Tests trotzdem. Sie
  importieren `Base`/`get_db` aus `app.db`, und `db.py` prüft die Variable beim Import – ohne
  `.env` bricht `python -m pytest` deshalb schon beim Collect ab, allerdings mit einer klaren
  Meldung (siehe „Datenbank"). Eine Verbindung wird dabei nicht aufgebaut, `create_engine`
  verbindet erst bei Bedarf.
  Fixtures legen jetzt erst `Artist`- und `Stage`-Zeilen an und referenzieren sie aus `Act`.
  Nicht offensichtlich: In-Memory-SQLite existiert nur pro Verbindung – deshalb mit
  `poolclass=StaticPool`, damit alle Sessions dieselbe Datenbank sehen.

## Aktuell nicht vorhanden (kein grundsätzliches Verbot mehr, nur noch kein Bedarf)

- `schemas.py`, `services/`, Repository-Klassen, Paket-Split (`app/api/`, `app/domain/`,
  `app/infra/`, …) – bei 7 flachen Modulen noch kein klarer Vorteil; siehe
  „Erweiterungspunkte" für die Bedingungen, unter denen das sinnvoll wird. Die
  Pydantic-Antwortmodelle stehen deshalb weiter in `routers.py`, dem einzigen Nutzer (T-15).
- `config.py` – `.env` gibt es inzwischen (`DATABASE_URL`), aber nur eine einzige Variable,
  direkt in `db.py` gelesen; ein eigenes Konfigurationsmodul lohnt sich erst bei mehreren
  Werten oder mehreren Umgebungen. Die Zeitzone bleibt eine Konstante im Code.
- Alembic-Migrationen – kommt, sobald Schemaänderungen nicht mehr per Löschen und
  Neu-Seeden gelöst werden sollen (z. B. produktive Daten, die erhalten bleiben müssen).
- Jinja-Templates, npm/JS-Build-Tooling, Docker, `conftest.py` – kommen mit den jeweiligen
  Anforderungen (serverseitiges Rendering, JS-Build, Deployment, wachsende Testsuite). Der
  einzige Build-Schritt ist bisher der CSS-Build mit der Tailwind-CLI (siehe „Frontend").

## Erweiterungspunkte (nicht in der aktuellen Version)

- **Konflikterkennung** ist nicht Teil der bestätigten Anforderungen (nur O7, setzt Favoriten
  O4 voraus; laut Domain Model sind Überlappungen erlaubt). Käme sie hinzu, wäre sie eine
  weitere reine Funktion in `app/schedule.py` – erst nach Anpassung der Anforderungen.
- **Weitere Attribute:** Genre auf `Artist`, Kapazität/Standort auf `Stage` – durch die
  Entitätstrennung jetzt ohne Umbau von `Act` möglich (siehe `domain-model.md`).
- **Paket-Split (`app/api/`, `app/domain/`, `app/infra/`, …):** sinnvoll, sobald einzelne
  Module wachsen (z. B. mehrere Router-Dateien, mehrere Domain-Module) oder neue fachliche
  Bereiche dazukommen. Die heutige Verantwortlichkeiten-Tabelle oben ist bereits die
  Layer-Zuordnung (`main.py` = Composition Root, `routers.py` = API, `crud.py` = Data Access,
  `models.py`/`schedule.py` = Domain, `db.py` = Infrastruktur) – ein Split würde bestehende
  Dateien nur in Unterpakete gruppieren, ohne ihre Verantwortung zu ändern.
