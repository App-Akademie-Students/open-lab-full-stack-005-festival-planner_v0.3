# Anforderungen

Status: Entwurf v0.3, Stand 2026-09-25 – teilweise umgesetzt: Mehrtägigkeit mit Tagesfilter
(C6, F6, Tages-Teil von B6), Tailwind CSS/responsive (C10, F4, F9), Favoriten merken (C7, F7),
persönlicher Zeitplan (C8, F8) und semantische Suche nach Acts (C11, F11, B8, B9, T4) über
US-7 bis US-11. Mehrere Festivals, Import und Offline-Verfügbarkeit sind noch nicht umgesetzt.
Neu aufgenommen, noch nicht umgesetzt: generierte Antwort auf Basis der Suchtreffer (C12, F12,
B10, T5 sowie Ergänzung von T1) – Phase 2 der Vektorsuche (LLM/RAG).
Vorherige bestätigte Stände sind eingefroren unter
[`requirements-history/requirements-v0.2.md`](requirements-history/requirements-v0.2.md)
(eintägiges Festival, ein Festival pro Instanz, kein Build-Tooling) und
[`requirements-history/requirements-v0.1-mvp.md`](requirements-history/requirements-v0.1-mvp.md)
(noch SQLite-Fassung von B2 und T1).
In v0.3 kommen mehrere Festivals, Mehrtägigkeit, Favoriten mit persönlichem Zeitplan,
Datenimport, Tailwind CSS und Offline-Verfügbarkeit hinzu. Dafür wurden C4, F4 und T1 sowie die
Scope-Abgrenzung angepasst; O1 (Tagesfilter) und O4 (Favoriten) sind in Muss-Anforderungen
aufgegangen.

## Grundannahme

Der Festival Planner beantwortet genau eine Frage: **Wo läuft was zu welcher Zeit?**
Die semantische Suche (C11) hilft beim „was": Besucher finden passende Acts, auch wenn sie
deren Namen nicht kennen. Auf Wunsch fasst eine generierte Antwort (C12) die gefundenen Acts
zu einer Antwort auf die Frage des Besuchers zusammen – ausschließlich auf Basis dieser Treffer.

Mehrere Festivals, jedes mit einem oder mehreren Tagen. Die Programmdaten werden per
Seed-Skript befüllt oder über das Backend importiert.
Besucher brauchen keinen Login. Persönliche Daten (Favoriten) bleiben ausschließlich im
Browser des Besuchers.

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
| C4 | Eine Instanz bildet mehrere Festivals ab; ein Festival kann einen oder mehrere Tage umfassen. |
| C5 | Ein Besucher wählt aus, welches Festival angezeigt wird. |
| C6 | Ein Besucher kann sich bei einem mehrtägigen Festival auf einen einzelnen Tag konzentrieren. |
| C7 | Ein Besucher kann Acts als Favoriten merken, ohne sich anzumelden. |
| C8 | Ein Besucher sieht seinen persönlichen Zeitplan: welche gemerkten Acts wann auf welcher Bühne spielen. |
| C9 | Ein Besucher kann das Programm auch ohne Netzverbindung einsehen (z. B. bei schlechtem Empfang auf dem Gelände). |
| C10 | Die Oberfläche ist auf dem Smartphone wie am Desktop übersichtlich und leicht bedienbar. |
| C11 | Ein Besucher findet Acts, indem er in eigenen Worten beschreibt, was er sucht (z. B. „ruhige elektronische Musik") – auch wenn diese Worte nicht wörtlich in den Programmdaten vorkommen. Die passendsten Acts stehen oben. |
| C12 | Ein Besucher kann sich zu seiner Suche auf Wunsch eine kurze Antwort in natürlicher Sprache geben lassen (z. B. auf „Wo kann ich tanzen?"), die seine Frage anhand der gefundenen Acts beantwortet. Die Antwort enthält nur Informationen aus den Festivaldaten; was dort nicht steht, wird nicht behauptet. |

### Frontend

| #  | Anforderung |
|----|-------------|
| F1 | Das Programm wird als chronologisch sortierte Liste angezeigt (Titel, Bühne, Startzeit, Endzeit). |
| F2 | Die Liste kann nach Bühne gefiltert werden. |
| F3 | „Läuft jetzt" und „kommt als Nächstes" werden anhand der aktuellen Zeit hervorgehoben. |
| F4 | Die Oberfläche ist eine einfache, mobiltaugliche HTML/Vanilla-JS-Seite ohne JS-Framework und ohne JS-Build-Tooling. Einziger Build-Schritt ist die Erzeugung des CSS (F9). |
| F5 | Das Festival kann ausgewählt werden; Programm, Bühnen und Tage beziehen sich auf das gewählte Festival. |
| F6 | Die Liste ist nach Tag gruppiert und kann auf einen Tag gefiltert werden. |
| F7 | Acts können als Favorit markiert und wieder entfernt werden. Favoriten werden clientseitig im Browser gespeichert und bleiben über ein Neuladen der Seite erhalten. |
| F8 | Ein kompakter Bereich oberhalb des Programms zeigt den persönlichen Zeitplan: nur die Favoriten, chronologisch sortiert (Titel, Bühne, Startzeit, Endzeit). Er zeigt immer alle Favoriten, unabhängig von Tages- und Bühnenfilter; ohne Favoriten erscheint ein Hinweis. Der Bereich lässt sich auf- und zuklappen und ist beim Laden der Seite zugeklappt. |
| F9 | Die Oberfläche wird mit Tailwind CSS gestaltet und ist responsive (Smartphone bis Desktop). |
| F10 | Nach einmaligem Laden sind Seite und zuletzt geladene Programmdaten auch ohne Netzverbindung verfügbar. |
| F11 | Ein Suchfeld nimmt eine frei formulierte Suchanfrage entgegen. Nach dem Absenden erscheint eine Liste passender Acts, sortiert nach semantischer Ähnlichkeit zur Anfrage (ähnlichster zuerst), je Treffer Titel, Bühne, Tag, Startzeit und Endzeit. Bei leerer Anfrage erscheint ein Hinweis statt einer Suche, bei fehlenden Treffern ein Hinweis, dass nichts Passendes gefunden wurde. |
| F12 | Liefert eine Suche (F11) Treffer, erscheint ein Button „Antwort generieren". Erst ein Klick darauf fordert die generierte Antwort an (C12, B10); währenddessen erscheint ein Ladehinweis. Die Antwort wird über der Trefferliste angezeigt, die Trefferliste bleibt sichtbar. Ohne Treffer erscheint kein Button. Ist keine Antwort verfügbar (B10), erscheint statt der Antwort ein Hinweis, dass sie gerade nicht verfügbar ist; die Treffer bleiben unverändert. Eine neue Suche entfernt eine vorherige Antwort. |

### Backend

| #  | Anforderung |
|----|-------------|
| B1 | Eine HTTP-API liefert die Programmpunkte, chronologisch sortiert und optional nach Bühne gefiltert. |
| B2 | Die Programmdaten werden in einer PostgreSQL-Datenbank (über SQLAlchemy) gespeichert. Die Verbindung ist konfigurierbar und nicht im Code verdrahtet. |
| B3 | Ein Seed-Skript befüllt die Datenbank initial. |
| B4 | Zeiten werden als vollständige Zeitstempel (Datum + Uhrzeit) gespeichert, nicht nur als Uhrzeit. |
| B5 | Das Datenmodell kennt Festivals (Name, Zeitraum); Bühnen und Acts gehören zu genau einem Festival. |
| B6 | Die API liefert die Liste der Festivals und das Programm je Festival, optional zusätzlich nach Tag gefiltert. |
| B7 | Über einen Backend-Zugang können Programmdaten (Festivals, Bühnen, Artists, Acts) importiert werden, ohne das Seed-Skript auszuführen. Der Zugang ist nicht für Besucher gedacht und gegen unberechtigte Nutzung geschützt. |
| B8 | Die API nimmt eine Suchanfrage in natürlicher Sprache entgegen und liefert die passenden Acts, absteigend nach semantischer Ähnlichkeit zur Anfrage sortiert. Durchsucht wird der Artist: Die Ähnlichkeit wird über Vektor-Repräsentationen (Embeddings) der Anfrage und der Artist-Daten aus B9 (Name, Genre, Beschreibung) bestimmt; die Suche läuft in der PostgreSQL-Datenbank. Bühne und Zeiten fließen nicht in den Vergleich ein, sondern werden über die Acts des gefundenen Artists ergänzt – Treffer sind die Acts der passenden Artists. Gesucht werden die 5 ähnlichsten Artists (feste Höchstzahl, keine Mindest-Ähnlichkeit); alle ihre Acts erscheinen als Treffer, unabhängig von Tages- oder Bühnenfilter des Programms, auch bereits vergangene Acts. Die Suche selbst generiert keinen Text – ihr Ergebnis ist ausschließlich eine Liste vorhandener Acts; eine generierte Antwort gibt es nur auf ausdrückliche Anforderung (B10). |
| B9 | Zu jedem Artist werden neben dem Namen ein Genre und eine kurze Beschreibung gespeichert. Name, Genre und Beschreibung bilden zusammen den Suchinhalt der semantischen Suche (B8). |
| B10 | Die API nimmt eine Anfrage in natürlicher Sprache entgegen und liefert eine per Sprachmodell (LLM) generierte Antwort darauf. Grundlage (Kontext) der Antwort sind ausschließlich die Treffer der semantischen Suche (B8) zur selben Anfrage, mit den Artist-Daten aus B9 sowie Bühne, Tag, Startzeit und Endzeit der Acts. Zu jedem Act enthält der Kontext außerdem, ob er bereits vorbei ist, gerade läuft oder noch kommt (bezogen auf die aktuelle Festival-Zeit, T3), damit die Antwort keine vergangenen Acts als bevorstehend darstellt. Die Antwort nennt nur Acts, Bühnen und Zeiten, die im Kontext stehen, und erfindet keine Festivalinformationen; lässt sich die Frage aus dem Kontext nicht beantworten, sagt die Antwort das. Liefert die Suche keine Treffer, wird kein LLM aufgerufen. Ist das LLM nicht erreichbar oder überschreitet es ein Zeitlimit, liefert die API eine erkennbare „nicht verfügbar"-Antwort statt eines generierten Texts; die Suche (B8) bleibt davon unberührt. Jede Anfrage wird einzeln beantwortet, ohne Gesprächsverlauf. |

### Tech / nicht-funktional

| #  | Anforderung |
|----|-------------|
| T1 | Stack ausschließlich: FastAPI, SQLAlchemy, PostgreSQL, HTML, Vanilla JS, Tailwind CSS – keine weiteren Frameworks oder Dependencies. Für den Datenbankzugriff und die Konfiguration kommen `psycopg` (v3) und `python-dotenv` hinzu. Tailwind CSS wird ausschließlich über die Tailwind-CLI zur Erzeugung des CSS verwendet. Für die semantische Suche (C11, B8) kommen die PostgreSQL-Erweiterung pgvector (mit dem Python-Paket `pgvector`) und das mehrsprachige Embedding-Modell `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` hinzu, lokal ausgeführt über das Paket `sentence-transformers` (mit PyTorch). Für die generierte Antwort (C12, B10) kommt das Sprachmodell `qwen3-instruct:4b` hinzu, lokal ausgeführt über Ollama. Ausnahme: pytest + httpx als reine Dev-Dependencies für Tests. |
| T2 | Die Anwendung ist lokal als ein Prozess startbar (uvicorn). |
| T3 | Die „aktuelle Zeit" für F3 wird serverseitig in einer festen Festival-Zeitzone bestimmt: fester Offset UTC+02:00. |
| T4 | Die semantische Suche unterstützt Suchanfragen auf Deutsch: Deutsch formulierte Anfragen, auch umgangssprachlich und ohne exakte Begriffe aus den Programmdaten, liefern passende Acts. |
| T5 | Die generierte Antwort (B10) ist auf Deutsch. Das Sprachmodell läuft lokal; Anfragen und Festivaldaten werden an keinen externen Dienst übertragen. |

**Erweiterbarkeit (Leitplanke):**
B4 (vollständige Zeitstempel) trägt die Mehrtägigkeit samt Tagesfilter (F6) ohne eigene
Tag-Entität und ohne Datenmodell-Umbau. Die Trennung in `Artist`/`Stage`/`Act` (v0.2) hält
zusätzlich weitere Attribute offen (z. B. Genre auf `Artist`, Kapazität auf `Stage` – Richtung
O2), ebenfalls ohne Umbau von `Act`. Details:
[`architecture.md`](architecture.md#erweiterungspunkte-nicht-in-der-aktuellen-version).

**Offene Punkte (vor der Umsetzung zu klären):**

- F3/T3 bei Offline-Nutzung (F10): Der Status „läuft jetzt / kommt als Nächstes" wird
  serverseitig berechnet und ist offline nicht aktuell. Soll er offline clientseitig berechnet
  oder als veraltet gekennzeichnet werden?
- T3 bei mehreren Festivals (C4): Gilt UTC+02:00 weiterhin für alle Festivals, oder bekommt
  jedes Festival eine eigene Zeitzone?
- B7: Form des Imports (Datenformat, Endpunkt oder Skript) und Art des Zugriffsschutzes.
- B5: Gehört ein `Artist` zu einem Festival oder wird er festivalübergreifend geteilt?
- B7/B8: Wie kommen importierte Artists zu ihrem Embedding (beim Import automatisch oder per
  separatem Befehl wie nach dem Seed)?

## Optionale Anforderungen (später)

- O2 – Detailansicht pro Programmpunkt (Beschreibung, Genre).
- O3 – Exakte Freitextsuche nach Act-Namen (unabhängig von der semantischen Suche C11).
- O5 – Zeitraster-Ansicht statt Liste.
- O6 – Admin-Oberfläche zur Datenpflege.
- O7 – Konfliktanzeige paralleler Favoriten.
- O8 – Geländekarte.

## Typische Benutzeraktionen

1. Festival auswählen.
2. Programm öffnen und komplette Liste durchscrollen.
3. Auf einen Tag filtern.
4. Auf eine Bühne filtern.
5. „Was läuft jetzt?" prüfen.
6. „Was kommt als Nächstes?" (ggf. auf einer bestimmten Bühne) prüfen.
7. Acts als Favorit markieren oder wieder entfernen.
8. Persönlichen Zeitplan ansehen.
9. Programm ohne Netzverbindung ansehen.
10. Acts per Beschreibung suchen (z. B. „ruhige elektronische Musik").
11. Zu einer Suche eine generierte Antwort anfordern (z. B. „Wo kann ich tanzen?").

Betreiber: Programmdaten eines Festivals importieren.

## Scope-Abgrenzung – bewusst *nicht* in der aktuellen Version

- Keine Benutzerkonten und kein Login für Besucher.
- Keine serverseitige Personalisierung: Favoriten nur im Browser, keine geräteübergreifende
  Synchronisation, keine Benachrichtigungen.
- Keine Admin-/Redaktions-UI (Daten per Seed oder Import, B7).
- Keine Mehrsprachigkeit.
- Keine Karten-/Geo-Funktionen, keine Wegführung zwischen Bühnen.
- Keine Künstler-Profile, Bilder, Social Media.
- Keine Echtzeit-Updates/Push (Neuladen genügt).
- Keine native App – nur eine simple Weboberfläche.
- Keine Orts- oder Zeitangaben in der semantischen Suche: Bühne, Tag und Uhrzeit sind nicht
  Teil des Suchinhalts (B8, B9), eine Anfrage wie „heute Abend auf der Hauptbühne" wird also
  nicht über die Suche beantwortet.
- Kein Chat: Die generierte Antwort (B10) beantwortet jeweils eine einzelne Anfrage, ohne
  Gesprächsverlauf und ohne Folgefragen.
- Keine generierte Antwort ohne Grundlage: Das LLM beantwortet nur, was sich aus den
  Suchtreffern ergibt. Fragen, deren Antwort nicht in den Treffern steht (z. B. „Was läuft heute
  Abend?", weil die Suche nicht nach Zeit filtert, oder allgemeine Fragen wie Anreise oder
  Tickets), werden nicht aus Allgemeinwissen beantwortet.
