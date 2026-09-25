# Code Challenge: AI Quality Check

## Festival Planner mit semantischer Vektorsuche

> Ausfüllbares Review-Protokoll für eine Code-Challenge von etwa 45–60 Minuten.

## Review-Daten

| Feld | Eintrag |
|---|---|
| Datum | |
| Reviewende Person / Team | |
| Repository / Branch | |
| Commit | |
| Testumgebung | |

## Ziel

Der Festival Planner wird systematisch geprüft. Neben der normalen Funktionalität geht es besonders um die Frage, ob die semantische Suche fachlich sinnvolle, nachvollziehbare und robuste Ergebnisse liefert.

---

## 1. Funktionsprüfung

- [ ] Anwendung startet ohne Fehler.
- [ ] Festival-Line-up wird angezeigt.
- [ ] Acts können dem persönlichen Plan hinzugefügt werden.
- [ ] Acts können aus dem Plan entfernt werden.
- [ ] Zeitkonflikte werden erkannt.
- [ ] Der persönliche Plan bleibt gespeichert.
- [ ] Die semantische Suche kann ausgeführt werden.
- [ ] Suchergebnisse werden korrekt im Frontend angezeigt.

### Beobachtungen

- 

---

## 2. Embeddings

- [ ] Für alle relevanten Artists existiert ein Embedding.
- [ ] Jedes Embedding besitzt 384 Dimensionen.
- [ ] Für den Embedding-Text werden `name`, `genre` und `description` verwendet.
- [ ] Der erzeugte Embedding-Text ist einheitlich aufgebaut.
- [ ] Fehlende optionale Texte verursachen keinen Fehler.
- [ ] Embeddings werden gespeichert und nicht bei jeder Suche vollständig neu erzeugt.
- [ ] Das verwendete Embedding-Modell ist zentral konfiguriert oder dokumentiert.

### Stichprobe

| Artist | Genre vorhanden | Beschreibung vorhanden | Embedding vorhanden | 384 Dimensionen | Bemerkung |
|---|---:|---:|---:|---:|---|
| | ☐ | ☐ | ☐ | ☐ | |
| | ☐ | ☐ | ☐ | ☐ | |
| | ☐ | ☐ | ☐ | ☐ | |

---

## 3. Qualität der semantischen Suche

Führt mindestens fünf unterschiedliche Suchanfragen aus. Bewertet nicht nur, ob technisch Treffer geliefert werden, sondern auch, ob sie inhaltlich passen.

### Vorgeschlagene Suchanfragen

- `elektronische Musik`
- `ruhige Musik am Nachmittag`
- `Rockmusik`
- `Musik zum Tanzen`
- eine englische Suchanfrage
- eine ungewöhnliche oder fachfremde Suchanfrage

### Testprotokoll

Bewertung: **0 = unbrauchbar**, **1 = schwach**, **2 = teilweise passend**, **3 = gut passend**

| Nr. | Query | Erwartung | Tatsächliche Treffer | Bewertung 0–3 | Beobachtung |
|---:|---|---|---|---:|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

### Regeln der Suche

- [ ] Es werden höchstens die fünf ähnlichsten Artists berücksichtigt.
- [ ] Der definierte Mindestwert von 0,3 wird korrekt angewendet.
- [ ] Treffer unterhalb des Mindestwerts werden nicht angezeigt.
- [ ] Die Ergebnisse sind nach Relevanz beziehungsweise Ähnlichkeit sortiert.
- [ ] Zu den gefundenen Artists werden die richtigen Acts geliefert.
- [ ] Artists ohne Embedding werden kontrolliert ignoriert.
- [ ] Interne Embedding-Vektoren werden nicht an das Frontend übertragen.

> Wichtig: Prüft im Code, ob der Wert `0,3` als **Ähnlichkeit** oder als **Distanz** behandelt wird. Bei `<=>` liefert pgvector eine Kosinusdistanz; Ähnlichkeit und Distanz dürfen nicht verwechselt werden.

---

## 4. Grenzfälle und Robustheit

| Testfall | Erwartetes Verhalten | Ergebnis | OK |
|---|---|---|---:|
| Leere Query | verständliche Validierung oder leere Trefferliste | | ☐ |
| Nur Leerzeichen | wie leere Query | | ☐ |
| Sehr lange Query | kontrollierte Verarbeitung oder Begrenzung | | ☐ |
| Sonderzeichen | kein Serverfehler | | ☐ |
| Deutsche Query | sinnvolle Verarbeitung | | ☐ |
| Englische Query | sinnvolle Verarbeitung | | ☐ |
| Query ohne Festivalbezug | keine oder nachvollziehbar schwache Treffer | | ☐ |
| Artist ohne Description | kein Serverfehler | | ☐ |
| Artist ohne Genre | kein Serverfehler | | ☐ |
| Artist ohne Embedding | wird ignoriert oder gezielt behandelt | | ☐ |
| Datenbank ohne Artists | leere Trefferliste | | ☐ |
| Embedding-Modell nicht verfügbar | kontrollierte Fehlermeldung | | ☐ |
| Datenbank nicht verfügbar | kontrollierte Fehlermeldung | | ☐ |

---

## 5. Datenbank und pgvector

- [ ] Die PostgreSQL-Erweiterung `vector` ist aktiviert.
- [ ] `Artist.embedding` verwendet `vector(384)`.
- [ ] Embeddings werden korrekt gespeichert.
- [ ] `NULL`-Embeddings werden von der Suche ausgeschlossen.
- [ ] Der Operator `<=>` wird bewusst als Kosinusdistanz eingesetzt.
- [ ] Der Query-Vektor wird sicher parametrisiert an die Datenbank übergeben.
- [ ] Das Ergebnislimit wird serverseitig angewendet.
- [ ] Die Mindestschwelle wird serverseitig angewendet.
- [ ] Datenbankmigration oder Setup-Schritte sind dokumentiert.

### SQL-/Datenbank-Beobachtungen

- 

---

## 6. API-Prüfung

### Getesteter Endpunkt

```text
Methode / URL:
Query:
Statuscode:
```

- [ ] Der HTTP-Status ist passend.
- [ ] Die JSON-Struktur ist konsistent.
- [ ] Es werden nur benötigte Daten geliefert.
- [ ] Eine leere Trefferliste ist eine gültige Antwort.
- [ ] Fehlerhafte Requests erhalten eine verständliche Client-Fehlermeldung.
- [ ] Interne Fehler geben keine sensiblen Details preis.
- [ ] Die API-Dokumentation entspricht dem tatsächlichen Verhalten.

### Beispielantwort / Beobachtung

```json
{}
```

---

## 7. Backend- und Codequalität

- [ ] Die Erzeugung von Embeddings ist in einem eigenen Modul gekapselt.
- [ ] Das Embedding-Modell wird lazy geladen und wiederverwendet.
- [ ] Das Modell wird nicht bei jeder Query neu geladen.
- [ ] Datenbanklogik liegt nicht direkt im Router.
- [ ] Der Search-Endpoint besitzt eine klare Verantwortung.
- [ ] Validierung und Fehlerbehandlung sind nachvollziehbar.
- [ ] Funktionen und Variablen sind verständlich benannt.
- [ ] Es gibt keine auffällige Code-Duplizierung.
- [ ] Modellname, Dimension, Limit und Schwellenwert sind nicht verstreut hart codiert.
- [ ] Kommentare erklären das Warum und wiederholen nicht nur den Code.
- [ ] Abhängigkeiten sind vollständig in der Projektkonfiguration erfasst.

### Positiver Codebefund

- 

### Mögliche Verbesserung

- 

---

## 8. Automatisierte Tests

### Vorhandene Tests

- [ ] Normale Suche mit Treffern
- [ ] Top-5-Begrenzung
- [ ] Mindestwert 0,3
- [ ] Keine passenden Treffer
- [ ] Artist ohne Embedding
- [ ] Leere oder ungültige Query
- [ ] Search-API
- [ ] Datenbankzugriff
- [ ] Embedding-Funktion beziehungsweise Embedding-Text
- [ ] Fehlerfall des Embedding-Modells

### Testebenen richtig getrennt

- [ ] Reine Logik wird mit Unit-Tests geprüft.
- [ ] Das Embedding-Modell kann in API-Tests ersetzt oder gemockt werden.
- [ ] Die echte Vektorabfrage wird gegen PostgreSQL mit pgvector integriert getestet.
- [ ] Tests hängen nicht unnötig von Netzwerkzugriffen ab.
- [ ] Testergebnisse sind reproduzierbar.

### Testergebnis

```text
Ausgeführter Befehl:
Bestanden:
Fehlgeschlagen:
Übersprungen:
```

### Wichtigster fehlender Test

- 

---

## 9. Fachliche AI-/ML-Qualität

- [ ] Gute Treffer sind für Menschen nachvollziehbar.
- [ ] Erwartete Artists erscheinen bei typischen Queries.
- [ ] Offensichtlich unpassende Artists werden nicht hoch gerankt.
- [ ] Deutschsprachige Queries funktionieren ausreichend gut.
- [ ] Kleine Umformulierungen führen zu vergleichbaren Ergebnissen.
- [ ] Schwache oder fehlende Treffer werden nicht als sichere Empfehlung dargestellt.
- [ ] Die Grenzen des verwendeten Modells sind dokumentiert.

### Vergleich durch Umformulierung

| Ausgangsquery | Umformulierung | Ergebnisse vergleichbar? | Beobachtung |
|---|---|---:|---|
| | | ☐ | |
| | | ☐ | |

### Auffälligkeiten

- Besonders gute Query:
- Besonders schlechte Query:
- Unerwarteter Treffer:
- Erwarteter, aber fehlender Treffer:

---

## 10. Findings

Priorität: **kritisch**, **hoch**, **mittel**, **niedrig**

| ID | Befund | Priorität | Reproduktion / Beleg | Empfohlene Maßnahme | Issue-Link |
|---|---|---|---|---|---|
| F-01 | | | | | |
| F-02 | | | | | |
| F-03 | | | | | |

---

## 11. Review-Ergebnis

### Was funktioniert gut?

- 

### Gefundene Probleme

- 

### Verbesserungsvorschläge

- 

### Fehlende Tests

- 

### Wichtigste Erkenntnis

- 

## Freigabeentscheidung

- [ ] **Freigabe** – keine wesentlichen Probleme gefunden.
- [ ] **Freigabe mit bekannten Einschränkungen** – Findings sind dokumentiert und vertretbar.
- [ ] **Änderungen erforderlich** – mindestens ein wesentlicher Befund muss behoben werden.

### Begründung

- 

### Nächste Schritte

| Maßnahme | Verantwortlich | Priorität / Termin | GitHub Issue |
|---|---|---|---|
| | | | |
| | | | |

---

## Abschluss der Code Challenge

Jedes Team nennt zum Schluss:

1. **einen positiven Punkt**,
2. **eine Verbesserung**,
3. **ein Risiko** und
4. **einen fehlenden Test**.

