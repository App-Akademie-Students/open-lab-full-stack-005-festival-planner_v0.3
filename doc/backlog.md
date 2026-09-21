# Backlog

Status: Stand 2026-09-21. v0.1 bestätigt und umgesetzt (Roadmap-Schritt 9). v0.2 ist
umgesetzt, in zwei Phasen: Refactoring Phase 1 (T-1 bis T-9, `Artist`/`Stage`/`Act` statt
`ProgramItem`) und Refactoring Phase 2 (T-10 bis T-13, Umstellung von SQLite auf PostgreSQL
bei Neon) – siehe die beiden Abschnitte unten.

Testen und Reviewen ist für beide Phasen erledigt und in [`review.md`](review.md)
freigegeben: Phase 1 in Abschnitt 6 (Stand 2026-09-16), die PostgreSQL-Umstellung in
Abschnitt 7 (Stand 2026-09-18). Beide Urteile: „Freigeben mit nicht blockierenden
Änderungswünschen", keine Blocker. T-19 bis T-21 aus dem Phase-2-Review sind inzwischen
umgesetzt, T-15 bis T-18 ebenfalls (2026-09-21) – aus beiden Reviews ist nichts mehr offen.

Für v0.3 (Entwurf der Anforderungen in [`requirements.md`](requirements.md)) sind bisher
US-7 (responsive Darstellung mit Tailwind CSS, umgesetzt) und US-8 (Programm nach Tag
gruppieren und filtern, umgesetzt) aufgenommen – siehe Abschnitt „v0.3" unten. Beide sind in
[`review.md`](review.md), Abschnitt 8 (Stand 2026-09-21), freigegeben: „Freigeben mit nicht
blockierenden Änderungswünschen", keine Blocker; die Änderungswünsche stehen als T-22 bis T-26
unter „Offene Punkte aus dem Review" (alle erledigt).

Abgeleitet aus den Muss-Anforderungen in [`requirements.md`](requirements.md).
Technischer Rahmen: [`architecture.md`](architecture.md).

## Übersicht

Reihenfolge = Priorität. Status: `offen` · `in Arbeit` · `erledigt`

| ID | Titel | Abhängig von | Anforderungen | Status |
|---|---|---|---|---|
| T-0 | Projektgerüst (technische Aufgabe) | – | B2, T2 | erledigt |
| US-1 | Programm einspielen | T-0 | B2, B3, B4, C4 | erledigt |
| US-2 | Programm als Liste sehen | US-1 | C1, F1, B1, T2 | erledigt |
| US-3 | Sehen, was gerade läuft | US-2 | C2, F3, T3 | erledigt |
| US-4 | Sehen, was als Nächstes kommt | US-2 | C2, F3 | erledigt |
| US-5 | Nach Bühne filtern | US-2 | C3, F2, B1 | erledigt |
| US-6 | Programm auf dem Smartphone nutzen | US-2 | F4, T1 | erledigt |

```text
T-0 ──▶ US-1 ──▶ US-2 ──┬──▶ US-3  „läuft jetzt"
                        ├──▶ US-4  „als Nächstes"
                        ├──▶ US-5  Bühnenfilter
                        └──▶ US-6  Mobil
```

Nach US-2 existiert eine lauffähige, bereits nützliche Version. US-3 bis US-6 hängen nur von
US-2 ab und sind untereinander unabhängig.

## Stories

### T-0 · Projektgerüst (technische Aufgabe)

Kein Nutzen für Besucher, aber Voraussetzung dafür, dass Start, Tests und Struktur
funktionieren, bevor Features gebaut werden.

- [x] Ordner und Dateien laut `architecture.md` sind angelegt (`app/`, `static/`, `tests/`),
      dazu `requirements-dev.txt` mit pytest und httpx.
- [x] `uvicorn app.main:app --reload` startet fehlerfrei; `/` liefert eine (noch leere) `index.html`.
- [x] `python -m pytest` läuft grün.

### US-1 · Programm einspielen

> Als **Betreiber** möchte ich das Festivalprogramm per Skript in die Datenbank laden,
> damit Besucher ohne Admin-Oberfläche echte Programmdaten sehen.

- [x] `python -m app.seed` legt das Schema in der über `DATABASE_URL` konfigurierten Datenbank
      an und füllt ca. 10–15 Programmpunkte auf 3 Bühnen.
- [x] Alle Punkte liegen auf dem heutigen Datum (Festival-Zeit) mit vollständigen Zeitstempeln –
      inklusive paralleler Acts auf verschiedenen Bühnen und mindestens zwei Acts mit gleicher Startzeit.
- [x] Jeder Punkt erfüllt die Invarianten: Titel und Bühne nicht leer, Ende nach Start.
- [x] Erneutes Ausführen ersetzt die Daten (keine Duplikate).

### US-2 · Programm als Liste sehen

> Als **Besucher** möchte ich das komplette Tagesprogramm als chronologische Liste sehen,
> damit ich weiß, welcher Act wann auf welcher Bühne spielt.

- [x] Die Startseite zeigt alle Programmpunkte mit Start- und Endzeit (HH:MM), Titel und Bühne – ohne Login.
- [x] Sortiert nach Startzeit; bei gleicher Startzeit alphabetisch nach Bühne.
- [x] `GET /api/program` liefert dieselben Punkte in derselben Reihenfolge als JSON.
- [x] Ist die Datenbank leer, zeigt die Seite einen Hinweis statt einer leeren Fläche.

### US-3 · Sehen, was gerade läuft

> Als **Besucher** möchte ich sofort sehen, was gerade läuft,
> damit ich weiß, wo ich jetzt hingehen kann.

- [x] Punkte mit `Start ≤ jetzt < Ende` sind als „läuft jetzt" hervorgehoben; mehrere gleichzeitig möglich.
- [x] Genau zur Startzeit gilt ein Act als „läuft jetzt", genau zur Endzeit nicht mehr.
- [x] „Jetzt" ist die serverseitige Festival-Zeit (UTC+02:00), nicht die Geräteuhr; sie wird auf der Seite angezeigt.
- [x] Aktualisierung durch Neuladen der Seite (kein Auto-Refresh).

### US-4 · Sehen, was als Nächstes kommt

> Als **Besucher** möchte ich sehen, was als Nächstes kommt,
> damit ich meinen nächsten Bühnenwechsel planen kann.

- [x] Die Punkte mit der frühesten Startzeit nach „jetzt" sind als „als Nächstes" hervorgehoben –
      bei gleicher Startzeit mehrere.
- [x] „Als Nächstes" ist optisch von „läuft jetzt" unterscheidbar.
- [x] Vor Festivalbeginn ist nichts „läuft jetzt", die ersten Acts sind „als Nächstes";
      nach dem letzten Act ist nichts hervorgehoben – ohne Fehler.

### US-5 · Nach Bühne filtern

> Als **Besucher** möchte ich das Programm auf eine Bühne einschränken,
> damit ich mich auf diese Bühne konzentrieren kann.

- [x] Ein Auswahlfeld bietet „Alle Bühnen" und alle Bühnen aus `GET /api/stages` (alphabetisch).
- [x] Die Auswahl zeigt nur Punkte dieser Bühne, weiterhin chronologisch; „Alle Bühnen" zeigt wieder alles.
- [x] `GET /api/program?stage=X` filtert serverseitig; eine unbekannte Bühne liefert eine leere Liste.
- [x] Sind US-3/US-4 umgesetzt, beziehen sich „läuft jetzt" und „als Nächstes" auf die gewählte Bühne.

### US-6 · Programm auf dem Smartphone nutzen

> Als **Besucher** möchte ich das Programm auf dem Smartphone bequem lesen,
> damit ich es auf dem Festivalgelände nutzen kann.

- [x] Bei 360 px Breite ist alles ohne horizontales Scrollen lesbar.
- [x] Der Bühnenfilter ist per Touch bedienbar.
- [x] Nur HTML, CSS und Vanilla JS – kein Build-Schritt.

## Abdeckung der Muss-Anforderungen

| Anforderung | Story | Anforderung | Story |
|---|---|---|---|
| C1 | US-2 | B1 | US-2, US-5 |
| C2 | US-3, US-4 | B2 | T-0, US-1 |
| C3 | US-5 | B3 | US-1 |
| C4 | US-1 | B4 | US-1 |
| F1 | US-2 | T1 | US-6, alle |
| F2 | US-5 | T2 | T-0, US-2 |
| F3 | US-3, US-4 | T3 | US-3 |
| F4 | US-6 | | |

## Definition of Done (für jede Story)

- Alle Akzeptanzkriterien erfüllt und im Browser geprüft.
- Neue Business-Logik in `app/schedule.py` ist in `tests/test_schedule.py` getestet;
  neue oder geänderte Endpunkte haben einen Test in `tests/test_api.py`.
- `python -m pytest` ist grün.
- Keine neuen Dependencies; Doku und `CLAUDE.md` sind aktuell, falls sich Entscheidungen geändert haben.
- Status in der Übersicht oben aktualisiert.

## v0.2 – Refactoring Phase 1 (Datenbank-Fokus)

Technische Aufgaben ohne direkten Besucher-Nutzen, Voraussetzung für spätere Erweiterungen
(z. B. Genre auf `Artist`, Kapazität auf `Stage`). Funktionalität und Datenbank bleiben in
dieser Phase unverändert (damals noch SQLite; die Umstellung auf PostgreSQL erfolgt erst in
Phase 2, T-10 bis T-13).
Details und Reihenfolge: [`roadmap.md`](roadmap.md) (Phase 2), technischer Rahmen:
[`architecture.md`](architecture.md).

| ID | Titel | Abhängig von | Status |
|---|---|---|---|
| T-1 | Domain Model erweitern (`Artist`, `Stage`, `Act`) | – | erledigt |
| T-2 | Architektur aktualisieren | T-1 | erledigt |
| T-3 | `app/models.py` anlegen | T-2 | erledigt |
| T-4 | API-Vertrag entscheiden (flach vs. verschachtelt) | T-3 | erledigt |
| T-5 | `app/seed.py` auf `Artist`/`Stage`/`Act` umstellen | T-4 | erledigt |
| T-6 | `app/crud.py` einführen (Queries mit Joins) | T-5 | erledigt |
| T-7 | `app/routers.py` einführen, `main.py` auf App-Setup reduzieren | T-6 | erledigt |
| T-8 | Tests umstellen (`tests/test_api.py` auf neue Modelle/Fixtures) | T-7 | erledigt |
| T-9 | `app/db.py` auf reine Infrastruktur reduzieren (`ProgramItem` entfernen) | T-8 | erledigt |

**T-4 – Entscheidung:** API-Vertrag bleibt flach (nicht verschachtelt). Begründung und
Beispiel: [`architecture.md`](architecture.md#http-api).

## v0.2 – Refactoring Phase 2 (Umstellung auf PostgreSQL)

Ebenfalls technische Aufgaben ohne direkten Besucher-Nutzen: die Datenhaltung wechselt von
der lokalen SQLite-Datei auf eine gehostete PostgreSQL-Datenbank (Neon). Funktionalität,
API-Vertrag und Frontend bleiben unverändert. Entscheidung und Begründung:
[`../CLAUDE.md`](../CLAUDE.md#project-decisions), technischer Rahmen:
[`architecture.md`](architecture.md#datenbank).

| ID | Titel | Abhängig von | Status |
|---|---|---|---|
| T-10 | `DATABASE_URL` aus `.env` laden (`python-dotenv`), Engine auf PostgreSQL umstellen | – | erledigt |
| T-11 | Treiber `psycopg` (v3): URL-Normalisierung in `db.py`, `requirements.txt` ergänzen | T-10 | erledigt |
| T-12 | `ends_at > starts_at` zusätzlich als DB-seitige `CheckConstraint` auf `Act` | T-10 | erledigt |
| T-13 | Doku nachziehen (`requirements.md` B2/T1, `domain-model.md`, `architecture.md`, `CLAUDE.md`, Backlog, Roadmap) | T-11, T-12 | erledigt |
| T-14 | Review-Nachtrag zur Umstellung in [`review.md`](review.md) ergänzen | T-13 | erledigt |

**T-10 bis T-12 – Entscheidungen:** `.env` ist nicht eingecheckt (siehe `.gitignore`); eine
`postgresql://`-URL wird in `db.py` auf `postgresql+psycopg://` normalisiert, weil SQLAlchemy
sonst `psycopg2` erwartet. Tests laufen weiterhin gegen In-Memory-SQLite, nicht gegen Neon.

## Offene Punkte aus dem Review (nicht blockierend)

Aus [`review.md`](review.md) (Abschnitte 2–4 und Nachträge). Keiner dieser Punkte verletzt eine
Muss-Anforderung; sie sind hier nur festgehalten, damit sie nicht verloren gehen.

Aus Abschnitt 6 (Phase 1):

| ID | Titel | Status |
|---|---|---|
| T-15 | TODO `# TODO move to rest_schema.py` in `app/routers.py` klären – widerspricht der dokumentierten „kein `schemas.py`"-Entscheidung; entweder entfernen oder als neue Entscheidung in `architecture.md` dokumentieren | erledigt |
| T-16 | Test-Overrides in `tests/test_api.py` von Modulebene in eine Fixture mit Teardown überführen | erledigt |
| T-17 | `StaticFiles`-Pfad in `app/main.py` unabhängig vom aktuellen Arbeitsverzeichnis auflösen | erledigt |
| T-18 | Invarianten `Artist.name` / `Stage.name` nicht leer als DB-`CheckConstraint` (analog T-12) | erledigt |

**T-15 bis T-18 – Umsetzung (2026-09-21):**

- T-15: TODO entfernt. `ProgramItemOut`/`ProgramResponse` werden nur in `routers.py` genutzt;
  ein `schemas.py` kommt erst mit konkretem Bedarf (siehe „Aktuell nicht vorhanden" in
  [`architecture.md`](architecture.md)), z. B. mehreren Router-Dateien.
- T-16: autouse-Fixture `override_dependencies` setzt die Overrides pro Test und entfernt sie
  danach wieder.
- T-17: `STATIC_DIR` wird relativ zu `app/main.py` aufgelöst; geprüft mit einem Start aus einem
  anderen Ordner (`uvicorn --app-dir …`).
- T-18: `CheckConstraint`s `trim(name) <> ''` auf `artists` und `stages` (auch reine
  Leerzeichen werden abgelehnt), Tests in `tests/test_models.py`. Damit die Constraints in
  einer bestehenden Datenbank ankommen, löscht `app/seed.py` die Tabellen jetzt und legt sie
  neu an (`drop_all` + `create_all`), statt nur die Zeilen zu löschen – `create_all` ändert
  bestehende Tabellen nicht. **In Neon wirksam erst nach einem erneuten `python -m app.seed`.**

Aus Abschnitt 7 (PostgreSQL-Umstellung) – alle drei umgesetzt am 2026-09-18:

| ID | Titel | Status |
|---|---|---|
| T-19 | Fehlende `DATABASE_URL` klar melden statt `KeyError`: `app/db.py` prüft die Variable und bricht mit Hinweis auf `.env` ab. Wichtig, weil ohne `.env` auch `python -m pytest` beim Collect abbricht – obwohl die Tests nur In-Memory-SQLite brauchen | erledigt |
| T-20 | `create_engine(..., pool_pre_ping=True)` gegen abgestandene Verbindungen nach Neons Idle-Suspend | erledigt |
| T-21 | Test für die `CheckConstraint` `ends_at > starts_at` (läuft auch unter In-Memory-SQLite) | erledigt |

Aus Abschnitt 8 (v0.3, US-7/US-8):

| ID | Titel | Status |
|---|---|---|
| T-22 | Status „läuft jetzt" / „als Nächstes" zusätzlich als Text-Badge anzeigen, nicht nur über Farbe (C2; wichtiger seit dem Tagesfilter, der auf späteren Tagen deren ersten Act als „als Nächstes" markiert) | erledigt |
| T-23 | Race Condition in `static/app.js` beheben: veraltete Antworten bei schnellem Filterwechsel verwerfen (`AbortController` oder Anfragezähler) | erledigt |
| T-24 | Leer-Hinweis unterscheiden: leere Datenbank vs. Filterkombination ohne Acts | erledigt |
| T-25 | Test für `build_acts()` in `app/seed.py`: Anzahl Tage, `ends_at > starts_at`, Acts über Mitternacht enden am Folgetag | erledigt |
| T-26 | `requirements.md` nachziehen: Statuszeile und Absatz „Erweiterbarkeit" behandeln Tagesfilter/Tailwind noch als nicht umgesetzt | erledigt |

**T-22/T-23 – Umsetzung (2026-09-21):** Text-Badge hinter dem Titel (`STATUS_BADGES` in
`static/app.js`, Klassen vollständig ausgeschrieben, `static/style.css` neu erzeugt).
Veraltete Antworten verwirft ein Anfragezähler (`latestProgramRequest`) – einfacher als
`AbortController` und ohne Fehlerbehandlung für abgebrochene Anfragen. Geprüft im Browser
(Headless-Chrome, 360 px und 1280 px) und für T-23 mit verzögert antwortendem Mock-`fetch`:
Die alte Version zeigt die vorletzte Auswahl, die neue die letzte. Automatisierte JS-Tests gibt
es bewusst nicht (kein JS-Build, keine JS-Test-Dependency).

**T-24/T-25 – Umsetzung (2026-09-21):** Der Leer-Hinweis in `static/app.js` hängt davon ab, ob
ein Filter gesetzt ist („Für diese Auswahl gibt es keine Acts." statt „Es sind noch keine
Programmpunkte vorhanden."); im Browser mit Mock-`fetch` geprüft. Neu ist `tests/test_seed.py`
mit 5 Tests für `build_acts()`. Gegenprobe: Ohne die Mitternachts-Korrektur in `build_acts()`
schlagen 2 davon fehl. Nicht geändert (Randnotiz aus dem Review, nur theoretisch): Ein Slot mit
gleicher Start- und Endzeit würde wegen `<=` zu einem 24-Stunden-Act.

**Hinweis:** Früher löschte `app/seed.py` per `DELETE`, sodass die PostgreSQL-Sequenzen beim
Neu-Seeden weiterliefen (siehe [`review.md`](review.md), Abschnitt 7). Seit T-18 legt der Seed
die Tabellen neu an; die `id`-Werte beginnen damit wieder bei 1.

Langfristig, ohne aktuellen Bedarf: `create_all` beim App-Start durch Migrationen ersetzen
(siehe „Aktuell nicht vorhanden" in [`architecture.md`](architecture.md)).

## v0.3 – Neue Anforderungen

Abgeleitet aus dem Entwurf v0.3 in [`requirements.md`](requirements.md). US-7, US-8 und
US-9 und US-10 sind umgesetzt; die übrigen neuen Anforderungen (C4 mehrere
Festivals, C5, C9, F5, F10, B5, B6 Festival-Teil, B7) sind noch nicht ins Backlog
übernommen. Die Festival-Entität (C4, C5, F5, B5) ist bis auf Weiteres zurückgestellt.

| ID | Titel | Abhängig von | Anforderungen | Status |
|---|---|---|---|---|
| US-7 | Responsive Darstellung mit Tailwind CSS | US-6 | C10, F4, F9, T1 | erledigt |
| US-8 | Programm nach Tag gruppieren und filtern | US-2 | C4 (Mehrtägigkeit), C6, F6, B4, B6 (Tagesfilter) | erledigt |
| US-9 | Acts als Favorit merken | US-2 | C7, F7 | erledigt |
| US-10 | Persönlicher Zeitplan über dem Programm | US-9 | C8, F8 | erledigt |

### US-7 · Responsive Darstellung mit Tailwind CSS

> Als **Besucher** möchte ich das Programm auf Smartphone und Desktop übersichtlich und leicht
> bedienbar sehen, damit ich mich auf jedem Gerät schnell zurechtfinde.

- [x] Die Oberfläche wird mit Tailwind CSS gestaltet; das bisherige eigene CSS ist dadurch ersetzt.
- [x] Das CSS wird mit der Tailwind-CLI aus den in `static/` verwendeten Klassen erzeugt; der
      Build-Befehl ist in `CLAUDE.md` unter „Project Commands" dokumentiert.
- [x] Kein JS-Framework und kein JS-Build – das Frontend bleibt HTML + Vanilla JS; der CSS-Build
      ist der einzige Build-Schritt (F4). Löst das US-6-Kriterium „kein Build-Schritt" ab.
- [x] Bei 360 px Breite ist alles ohne horizontales Scrollen lesbar; auf Desktop-Breite
      (ab 1024 px) bleibt die Liste übersichtlich und nutzt die Breite sinnvoll.
- [x] Bühnenfilter und alle weiteren Bedienelemente sind per Touch bedienbar.
- [x] Funktionen bleiben unverändert: chronologische Liste, Bühnenfilter, „läuft jetzt" und
      „als Nächstes" sind hervorgehoben und optisch voneinander unterscheidbar.
- [x] Entschieden und dokumentiert ist, ob die erzeugte CSS-Datei eingecheckt oder beim
      Setup gebaut wird, und woher die Tailwind-CLI kommt.

**US-7 – Entscheidung:** `static/style.css` wird eingecheckt, damit die App ohne Build-Schritt
startet; die Tailwind-CLI (v4, Standalone-Binary ohne Node) braucht nur, wer das Frontend
ändert. Details: [`../CLAUDE.md`](../CLAUDE.md#project-decisions).

**Hinweis zur Definition of Done:** „Keine neuen Dependencies" gilt für US-7 mit der Ausnahme
Tailwind CSS (Tailwind-CLI), die T1 ausdrücklich erlaubt.

### US-8 · Programm nach Tag gruppieren und filtern

> Als **Besucher** möchte ich das Programm eines mehrtägigen Festivals nach Tagen gegliedert
> sehen und auf einen Tag einschränken, damit ich mich auf einen einzelnen Tag konzentrieren kann.

- [x] Das Seed-Skript legt ein Programm über mindestens zwei aufeinanderfolgende Tage an,
      beginnend mit dem heutigen Datum (Festival-Zeit), damit Gruppierung und Filter prüfbar sind.
- [x] Ohne Tagesfilter ist die Liste nach Tag gruppiert: pro Tag eine Überschrift mit Wochentag
      und Datum (z. B. „Fr, 18.09."), darunter die Acts dieses Tages chronologisch.
- [x] Ein Auswahlfeld bietet „Alle Tage" und alle Tage, an denen Acts stattfinden
      (chronologisch); die Auswahl zeigt nur die Acts dieses Tages.
- [x] Ein Act gehört zu dem Tag, an dem er beginnt (Festival-Zeit) – auch wenn er nach
      Mitternacht endet.
- [x] Tages- und Bühnenfilter sind kombinierbar; „läuft jetzt" und „als Nächstes" beziehen sich
      wie beim Bühnenfilter auf die gefilterte Liste.
- [x] `GET /api/program?day=YYYY-MM-DD` filtert serverseitig (kombinierbar mit `stage`); ein Tag
      ohne Acts liefert eine leere Liste. `GET /api/days` liefert die Tage mit Acts.
- [x] Hat das Festival nur einen Tag, bleibt die Anzeige übersichtlich (eine Tagesüberschrift,
      Auswahl mit nur einem Tag).
- [x] Tagesfilter und Tagesüberschriften sind auf dem Smartphone (360 px) per Touch bedienbar
      bzw. lesbar (F9).

**US-8 – Umsetzung:** Tagesregel als reine Funktionen `festival_day()`/`day_bounds()` in
`app/schedule.py`; `GET /api/days` und der `day`-Parameter in `app/crud.py`/`app/routers.py`;
Gruppierung und Tages-Dropdown in `static/app.js`. Bei Auswahl eines späteren Tages ist dessen
erster Act „als Nächstes" markiert – konsistent mit der Regel „Status nach dem Filter".
Details: [`architecture.md`](architecture.md#festivaltage).

### US-9 · Acts als Favorit merken

> Als **Besucher** möchte ich Acts als Favorit markieren, ohne mich anzumelden, damit ich mir
> merken kann, welche Acts ich sehen will.

- [x] Jeder Act in der Liste hat einen Favoriten-Schalter; ein Tippen markiert den Act als
      Favorit, ein erneutes Tippen entfernt die Markierung.
- [x] Favorit und Nicht-Favorit sind nicht nur über die Farbe unterscheidbar (Symbol ★/☆) und
      für Screenreader beschriftet.
- [x] Favoriten werden ausschließlich im Browser gespeichert (`localStorage`) und bleiben über
      ein Neuladen der Seite erhalten – kein Login, keine Übertragung an den Server.
- [x] Die Markierung gilt unabhängig von Tages- und Bühnenfilter: Ein Favorit bleibt markiert,
      wenn er nach einem Filterwechsel wieder angezeigt wird.
- [x] Ist der Browser-Speicher nicht verfügbar (z. B. privater Modus, blockiert), funktioniert
      die Seite weiter; Favoriten gelten dann nur bis zum Neuladen.
- [x] Der Schalter ist auf dem Smartphone (360 px) per Touch bedienbar (mind. 44 px), ohne
      horizontales Scrollen.

Nicht Teil von US-9: der persönliche Zeitplan als kompakter Bereich über dem Programm (C8, F8) –
siehe US-10.

**US-9 – Umsetzung (2026-09-21):** Nur Frontend (`static/app.js`), kein Backend-Umbau. Ein
Stern-Button pro Act (☆/★, `aria-pressed`, 44 px) schaltet den Favoriten um; gespeichert wird
ein Array von Act-`id`s unter dem Schlüssel `festival-planner.favorites` im `localStorage`.
Lesen und Schreiben stehen in `try/catch`, damit die Seite ohne Speicher weiterläuft. Auf dem
Smartphone rutscht die Bühne in eine eigene Zeile unter Zeit und Titel, weil der Stern den
Titel sonst so schmal drückt, dass Wörter mitten im Wort umbrechen.
**Entscheidung – Kennung:** die Act-`id` aus der API. Sie bleibt beim Neu-Seeden gleich (der
Seed ist deterministisch und legt die Tabellen neu an). Einschränkung: Werden Daten später
importiert oder geändert (B7), kann eine gespeicherte `id` auf einen anderen Act zeigen –
dann neu bewerten. Geprüft mit Headless-Chrome und Mock-`fetch`: Markieren, Filterwechsel,
Neuladen (Favorit bleibt), blockierter Speicher (Seite läuft, keine Fehler); Layout bei 360 px
und 1280 px mit echten Seed-Daten.

### US-10 · Persönlicher Zeitplan über dem Programm

> Als **Besucher** möchte ich meine gemerkten Acts kompakt oben auf der Seite sehen, damit ich
> ohne Suchen im ganzen Programm weiß, wann und wo meine Acts spielen.

- [x] Oberhalb des Programms steht ein kompakter Bereich mit allen Favoriten, chronologisch
      sortiert, je Eintrag Titel, Bühne, Start- und Endzeit sowie der Tag (Favoriten können
      über mehrere Festivaltage verteilt sein).
- [x] Der Bereich zeigt immer alle Favoriten, unabhängig von Tages- und Bühnenfilter.
- [x] Sind keine Favoriten gemerkt, zeigt der Bereich einen kurzen Hinweis, wie man Acts per
      Stern merkt.
- [x] Markieren oder Entfernen eines Favoriten in der Liste aktualisiert den Bereich sofort,
      ohne Neuladen.
- [x] Gespeicherte Favoriten-`id`s, zu denen es keinen Act mehr gibt, werden ohne Fehler
      ignoriert.
- [x] Der Bereich bleibt auf dem Smartphone (360 px) kompakt und lesbar, ohne horizontales
      Scrollen, und schiebt das Programm nicht unnötig weit nach unten.
- [x] Kein Backend-Umbau nötig, Favoriten bleiben ausschließlich im Browser (wie US-9).
- [x] Der Bereich ist ein Akkordeon: per Tippen auf die Kopfzeile auf- und zuklappbar, beim
      Laden der Seite zugeklappt. Die Kopfzeile zeigt auch zugeklappt die Anzahl der Favoriten
      und ist per Tastatur und Screenreader bedienbar (Touch-Ziel mind. 44 px).

**US-10 – Umsetzung (2026-09-21):** Nur Frontend (`static/index.html`, `static/app.js`,
neu erzeugtes `static/style.css`). **Entscheidung – Datenquelle:** Die Programmliste lädt
gefiltert, der Bereich braucht aber alle Acts. `app.js` ruft deshalb beim Seitenaufruf einmal
zusätzlich `GET /api/program` ohne Filter ab und filtert clientseitig auf die Favoriten; kein
neuer Endpunkt. Die Liste ist auf `max-h-60` begrenzt und scrollt bei vielen Favoriten intern.
Geprüft mit Headless-Chrome gegen die Seed-Daten: leerer Zustand (Hinweis), drei Favoriten über
zwei Tage plus eine unbekannte `id` (chronologisch, `id` ignoriert), Tages- und Bühnenfilter
gesetzt (Bereich unverändert), Stern setzen/entfernen (Bereich sofort aktualisiert), 360 px ohne
horizontales Scrollen.
**Änderung – Akkordeon (2026-09-21):** Natives `<details>`/`<summary>` ohne `open`-Attribut,
also zugeklappt beim Laden; kein zusätzliches JS für das Auf- und Zuklappen. Die Kopfzeile zeigt
„Meine Favoriten (n)". Der Zustand wird nicht gespeichert – nach dem Neuladen ist der Bereich
wieder zugeklappt. Geprüft mit Headless-Chrome: zugeklappt beim Laden, Aufklappen per Klick,
Anzahl aktualisiert sich beim Stern-Klick, Bereich bleibt dabei offen, 360 px ohne horizontales
Scrollen.

## Bewusst nicht im Backlog

Suche, Detailansicht, Admin-UI, Auto-Refresh, Konflikterkennung – siehe optionale
Anforderungen O2–O8 und Scope-Abgrenzung in [`requirements.md`](requirements.md).
