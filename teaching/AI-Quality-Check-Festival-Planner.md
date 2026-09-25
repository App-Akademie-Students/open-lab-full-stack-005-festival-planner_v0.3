# Code Challenge: AI Quality Check

## Ziel

Der Festival Planner mit semantischer Vektorsuche wird systematisch geprüft.

Dabei betrachten wir nicht nur:

- „Funktioniert die Anwendung?“

sondern auch:

- Liefert die semantische Suche sinnvolle Ergebnisse?
- Sind Grenzfälle berücksichtigt?
- Ist die Architektur nachvollziehbar?
- Ist der Code wartbar?
- Sind AI-Komponenten kontrollierbar und testbar?

---

## 1. Funktionaler Check

- [ ] Anwendung startet ohne Fehler
  - Problem / Beobachtung:
- [ ] Festival-Line-up wird angezeigt
  - Problem / Beobachtung:
- [ ] Acts können dem Plan hinzugefügt werden
  - Problem / Beobachtung:
- [ ] Acts können entfernt werden
  - Problem / Beobachtung:
- [ ] Konflikte werden erkannt
  - Problem / Beobachtung:
- [ ] Plan bleibt gespeichert
  - Problem / Beobachtung:
- [ ] Semantische Suche funktioniert
  - Problem / Beobachtung:
- [ ] Suchergebnisse werden korrekt im Frontend angezeigt
  - Problem / Beobachtung:

---

## 2. Vektorsuche

### Embeddings

- [x] Für alle relevanten Artists existiert ein Embedding
  - Beobachtung:
- [ ] Jedes Embedding hat 384 Dimensionen
  - Beobachtung:
- [ ] Name, Genre und Description werden verwendet
  - Beobachtung:
- [ ] Die Pflichtfelder `genre` und `description` werden durch Datenbankregeln und Tests validiert
  - Beobachtung:
- [ ] Artists ohne Embedding sind zulässig und werden von der Vektorsuche kontrolliert ausgeschlossen
  - Beobachtung:

### Suche

Testet mehrere unterschiedliche Suchanfragen.

- [ ] Query „elektronische Musik“ liefert sinnvolle Ergebnisse
  - Erwartung: elektronische Artists
  - Tatsächliche Treffer / Beobachtung:
- [ ] Query „ruhige Musik“ liefert sinnvolle Ergebnisse
  - Erwartung: passende ruhigere Artists
  - Tatsächliche Treffer / Beobachtung:
- [ ] Query „Rockmusik“ liefert sinnvolle Ergebnisse
  - Erwartung: Rock-Artists
  - Tatsächliche Treffer / Beobachtung:
- [ ] Query „Musik zum Tanzen“ liefert sinnvolle Ergebnisse
  - Erwartung: semantisch passende Artists
  - Tatsächliche Treffer / Beobachtung:
- [ ] Eine ungewöhnliche oder unsinnige Query wird sinnvoll behandelt
  - Erwartung: keine oder nur schwache Treffer
  - Tatsächliche Treffer / Beobachtung:

Zusätzlich prüfen:

- [ ] maximal **Top 5 Artists**
- [ ] Mindestähnlichkeit **0,3**
- [ ] Artists unterhalb des Mindestwerts werden nicht angezeigt
- [ ] Acts werden korrekt den gefundenen Artists zugeordnet
- [ ] Ergebnisse sind nach Ähnlichkeit sortiert

---

## 3. Grenzfälle

Was passiert bei:

- [ ] leerem Suchfeld?
- [ ] nur Leerzeichen?
- [ ] sehr langer Query?
- [ ] Sonderzeichen?
- [ ] deutscher Sprache?
- [ ] englischer Sprache?
- [ ] Query ohne semantischen Bezug zum Festival?
- [ ] leerem oder ungültigem Pflichtfeld `description`?
- [ ] leerem oder ungültigem Pflichtfeld `genre`?
- [ ] Datenbank ohne Artists?
- [ ] fehlendem Embedding?

Erwartung:

Die Anwendung sollte kontrolliert reagieren und nicht mit einem Serverfehler abbrechen.

---

## 4. Datenbank / pgvector

Prüfen:

- [ ] `vector`-Extension ist aktiviert
- [ ] `Artist.embedding` verwendet `vector(384)`
- [ ] Embeddings werden korrekt gespeichert
- [ ] `NULL`-Embeddings werden bei der Suche ignoriert
- [ ] `<=>` wird korrekt für die Distanzberechnung verwendet
- [ ] Query-Vektor wird korrekt an die Datenbank übergeben
- [ ] `LIMIT` wird serverseitig angewendet

---

## 5. Backend-Qualität

Prüfen:

- [ ] Embedding-Erzeugung ist gekapselt
- [ ] Embedding-Modell wird nicht bei jeder Query neu geladen
- [ ] Datenbanklogik liegt nicht direkt im Router
- [ ] Search-Endpoint hat eine klare Verantwortung
- [ ] Fehler werden sinnvoll behandelt
- [ ] Funktionen haben verständliche Namen
- [ ] unnötige Duplikation wurde vermieden
- [ ] Konfiguration ist nicht hart codiert

---

## 6. API-Check

Beispiel:

```http
GET /api/search?q=elektronische%20Musik
```

Prüfen:

- [ ] HTTP-Status korrekt
- [ ] JSON-Struktur konsistent
- [ ] nur benötigte Daten werden geliefert
- [ ] keine internen Embedding-Vektoren werden übertragen
- [ ] leere Trefferliste ist erlaubt
- [ ] fehlerhafte Requests liefern verständliche Fehler

---

## 7. Tests

Existieren Tests für:

- [ ] normale Suche
- [ ] Top-5-Begrenzung
- [ ] Mindestähnlichkeit 0,3
- [ ] keine Treffer
- [ ] Artist ohne Embedding
- [ ] leere Query
- [ ] Search-API
- [ ] Datenbankzugriff
- [ ] Embedding-Funktion

Zusatzfrage:

**Welche Teile lassen sich ohne echte pgvector-Datenbank testen und welche benötigen Integrationstests?**

---

## 8. AI-/ML-spezifischer Quality Check

Die wichtigste Frage:

> Liefert die Suche nur technisch korrekte oder auch fachlich sinnvolle Ergebnisse?

Dazu mehrere Queries ausprobieren und jeweils bewerten:

- [ ] Query 1 bewertet
  - Query:
  - Treffer:
  - Bewertung: plausibel / überraschend / falsch
- [ ] Query 2 bewertet
  - Query:
  - Treffer:
  - Bewertung: plausibel / überraschend / falsch
- [ ] Query 3 bewertet
  - Query:
  - Treffer:
  - Bewertung: plausibel / überraschend / falsch

Auffälligkeiten dokumentieren:

- Welche Query funktioniert besonders gut?
- Welche Query funktioniert schlecht?
- Welche Artists werden unerwartet gefunden?
- Welche erwarteten Artists fehlen?

---

## 9. Code Review

Sucht mindestens:

### Einen positiven Punkt

```text
Was ist gut gelöst?

```

### Eine Verbesserung

```text
Was könnte vereinfacht oder robuster gemacht werden?

```

### Ein Risiko

```text
Was könnte später zu Problemen führen?

```

### Einen fehlenden Test

```text
Welcher Test sollte ergänzt werden?

```

---

## 10. Ergebnis des Reviews

### Was funktioniert gut?

```text


```

### Gefundene Probleme

```text


```

### Verbesserungsvorschläge

```text


```

### Fehlende Tests

```text


```

### Wichtigste Erkenntnis

```text


```

---

## Abschlussfrage

**Würden wir diese Version nach unserem Review freigeben?**

- [ ] technisch funktionsfähig
- [ ] ausreichend getestet
- [ ] bekannte Risiken dokumentiert
- [ ] Verbesserungen als Issues festgehalten
