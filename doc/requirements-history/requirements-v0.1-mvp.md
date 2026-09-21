# Anforderungen – eingefroren: v0.1 MVP

Snapshot des bestätigten Anforderungsstands aus Roadmap-Schritt 6 (v0.1-MVP), vor dem
Domain-Modell-Refactor (`Artist`/`Stage`/`Act`, v0.2). Nur zur historischen Referenz –
maßgeblich ist [`../requirements.md`](../requirements.md).

## Grundannahme

Der Festival Planner beantwortet genau eine Frage: **Wo läuft was zu welcher Zeit?**

Ein Festival, ein Tag. Die Programmdaten werden per Seed-Skript befüllt.
Besucher konsumieren die Daten nur – kein Login, keine Personalisierung.

Die Muss-Anforderungen sind nach Sicht getrennt: **Customer** (fachlich/Nutzen),
**Frontend** (Weboberfläche), **Backend** (Server/API/Daten), **Tech** (Stack &
nicht-funktionale Rahmenbedingungen).

## Muss-Anforderungen

### Customer (fachlich)

| #  | Anforderung |
|----|-------------|
| C1 | Ein Besucher findet ohne Login und ohne Anleitung heraus, welcher Act wann auf welcher Bühne spielt. |
| C2 | Ein Besucher erkennt sofort, was gerade läuft und was als Nächstes kommt. |
| C3 | Ein Besucher kann sich auf eine einzelne Bühne konzentrieren. |
| C4 | Eine Instanz bildet genau ein eintägiges Festival ab. |

### Frontend

| #  | Anforderung |
|----|-------------|
| F1 | Das Programm wird als chronologisch sortierte Liste angezeigt (Titel, Bühne, Startzeit, Endzeit). |
| F2 | Die Liste kann nach Bühne gefiltert werden. |
| F3 | „Läuft jetzt" und „kommt als Nächstes" werden anhand der aktuellen Zeit hervorgehoben. |
| F4 | Die Oberfläche ist eine einfache, mobiltaugliche HTML/JS-Seite ohne Build-Tooling. |

### Backend

| #  | Anforderung |
|----|-------------|
| B1 | Eine HTTP-API liefert die Programmpunkte, chronologisch sortiert und optional nach Bühne gefiltert. |
| B2 | Die Programmdaten werden in SQLite (über SQLAlchemy) gespeichert. |
| B3 | Ein Seed-Skript befüllt die Datenbank initial. |
| B4 | Zeiten werden als vollständige Zeitstempel (Datum + Uhrzeit) gespeichert, nicht nur als Uhrzeit. |

### Tech / nicht-funktional

| #  | Anforderung |
|----|-------------|
| T1 | Stack ausschließlich: FastAPI, SQLAlchemy, SQLite, HTML, Vanilla JS – keine weiteren Frameworks oder Dependencies. Ausnahme: pytest + httpx als reine Dev-Dependencies für Tests. |
| T2 | Die Anwendung ist lokal als ein Prozess startbar (uvicorn). |
| T3 | Die „aktuelle Zeit" für F3 wird serverseitig in einer festen Festival-Zeitzone bestimmt: fester Offset UTC+02:00. |

**Erweiterbarkeit (Leitplanke, keine Umsetzung in der aktuellen Version):**
B4 (vollständige Zeitstempel) hält einen späteren Tagesfilter / Mehrtägigkeit als reine
Anzeige-Logik offen – kein Datenmodell-Umbau nötig.

## Optionale Anforderungen (später)

- O1 – Tagesfilter / Mehrtägigkeit.
- O2 – Detailansicht pro Programmpunkt (Beschreibung, Genre).
- O3 – Freitextsuche nach Act-Namen.
- O4 – Persönlicher Merkzettel / Favoriten (clientseitig).
- O5 – Zeitraster-Ansicht statt Liste.
- O6 – Admin-Oberfläche zur Datenpflege.
- O7 – Konfliktanzeige paralleler Favoriten.
- O8 – Geländekarte.

## Typische Benutzeraktionen

1. Programm öffnen und komplette Liste durchscrollen.
2. Auf eine Bühne filtern.
3. „Was läuft jetzt?" prüfen.
4. „Was kommt als Nächstes?" (ggf. auf einer bestimmten Bühne) prüfen.

## Scope-Abgrenzung – bewusst *nicht* in der aktuellen Version

- Keine Benutzerkonten, kein Login, keine Authentifizierung.
- Keine Personalisierung, kein serverseitiger Merkzettel, keine Benachrichtigungen.
- Keine Admin-/Redaktions-UI (Daten per Seed).
- Kein Tagesfilter / keine Mehrtägigkeit (nur als Datenmodell-Leitplanke vorbereitet).
- Keine Mehrsprachigkeit.
- Nur ein Festival pro Instanz.
- Keine Karten-/Geo-Funktionen.
- Keine Künstler-Profile, Bilder, Social Media.
- Keine Echtzeit-Updates/Push (Neuladen genügt).
- Keine native App – nur eine simple Weboberfläche.
