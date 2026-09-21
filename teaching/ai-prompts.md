# Promts
## 0)


Verschaffe dir bitte zuerst einen Überblick über den aktuellen Stand des Projekts.

1. Prüfe die `CLAUDE.md` auf Konsistenz mit dem aktuellen Projektstand und schlage nötige Anpassungen vor. Noch nichts ändern.
    
2. Was ist bereits umgesetzt?
    
3. Was haben wir zuletzt gemacht?
    
4. Gibt es aktuell offene, uncommittete oder unvollständige Änderungen?
    
5. Welche Aufgaben oder User Stories sind noch offen?
    
6. Was wäre jetzt der sinnvollste nächste Schritt?


## 1)

Wir arbeiten ab jetzt an Version 0.2 des Festival Planners.

Die bisherige Anwendung war als MVP angelegt. In mehreren Projektdateien und Beschreibungen wird deshalb noch der Begriff „MVP“ verwendet.

Bitte prüfe das gesamte Projekt und passe die Bezeichnungen so an, dass die aktuelle Version nicht mehr generell als MVP bezeichnet wird.

Regeln:

- Entferne „MVP“ dort, wo damit die aktuelle Anwendung oder Architektur bezeichnet wird.
    
- Verwende stattdessen je nach Kontext neutrale Begriffe wie „Festival Planner“, „aktuelle Version“, „Domain Model“, „Architecture“ oder „Implementation“.
    
- Wenn ausdrücklich die alte erste Version beschrieben wird, darf „MVP“ weiterhin verwendet werden.
    
- Ändere keine fachlichen Anforderungen, keine Architektur und keinen Programmcode.
    
- Führe ausschließlich diese begriffliche Bereinigung durch.
    
- Zeige mir anschließend kurz, welche Dateien du geändert hast und welche Formulierungen ersetzt wurden.


## 2)

Analysiere die bestehende Festival-Planner-Anwendung v0.2. Verändere noch keinen Code.

Untersuche:

- Projektstruktur und Verantwortlichkeiten von `main.py`, `db.py`, `schedule.py`, `seed.py`
    
- aktuelles Domain Model und SQLite-Struktur
    
- bestehende Beziehungen
    
- vermischte Verantwortlichkeiten
    
- betroffene Stellen für das geplante Refactoring
    

Ziel von Refactoring Phase 1:

- Funktionalität erhalten
    
- SQLite beibehalten
    
- `Artist`, `Stage`, `Act` als getrennte Entitäten
    
- neue Struktur mit `models.py`, `crud.py`, `routers.py`
    
- `schedule.py` möglichst als eigenständige Fachlogik erhalten
    

Erstelle eine kurze Ist-Analyse mit:

1. aktueller Architektur
    
2. aktuellem Domain Model
    
3. Problemen/Grenzen
    
4. betroffenen Dateien
    
5. empfohlenen nächsten Refactoring-Schritten
    

Noch keine Dateien ändern und keinen Code erzeugen.




Stelle Festival Planner v0.2 jetzt direkt von SQLite auf die bereits eingerichtete Neon-PostgreSQL-Datenbank um.

- `DATABASE_URL` liegt in `.env`.
    
- Prüfe `models.py` auf PostgreSQL-Kompatibilität.
    
- Passe `requirements.txt` und `db.py` für PostgreSQL/Neon an.
    
- Entferne SQLite-spezifische Konfiguration.
- Erzeuge die Tabellen direkt mit `Base.metadata.create_all()` in Neon.
    
- Prüfe anschließend Tabellen, Primär-/Fremdschlüssel, UNIQUE-Constraints und `ends_at > starts_at`.

- Führe die notwendigen Änderungen und Befehle selbstständig aus. Keine weiteren Architekturänderungen.

- Führe danach die Tests aus und fasse Änderungen und Ergebnis kurz zusammen.
- mache nach jedem Schritt eine kurzen Überprüfung stop und Bericht

## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## New Features with claude sub-agents
* Date: 2026-09-18

Erstelle für dieses Projekt drei projektbezogene Claude-Code-Subagents unter `.claude/agents/`.

Die Subagents sollen ausschließlich der Product Discovery dienen und keinen Anwendungscode verändern. Verwende für alle drei nur Read-only-Tools wie Read, Grep und Glob und als Modell Sonnet.

## 1. customer-opportunity

Aufgabe:  
Analysiere Kundenfeedback, Interviews, Support-Anfragen oder andere bereitgestellte Kundensignale.

Ziel:  
Identifiziere Probleme, Bedürfnisse, Wünsche und Jobs-to-be-Done, die als Opportunities im Sinne eines Opportunity Solution Tree betrachtet werden können.

Regeln:

- Noch keine Features oder Lösungen vorschlagen.
    
- Jede Opportunity muss auf konkreter Evidence aus dem Input beruhen.
    
- Ähnliche Kundenaussagen zusammenfassen.
    
- Annahmen und Unsicherheiten ausdrücklich kennzeichnen.
    
- Keine Kundenprobleme erfinden.
    

Output:

- erkannte Opportunities
    
- zugehörige Evidence
    
- betroffene Nutzerbedürfnisse
    
- offene Fragen bzw. Unsicherheiten
    

## 2. solution-designer

Aufgabe:  
Erhalte eine oder mehrere bereits identifizierte Opportunities und entwickle dafür unterschiedliche Lösungsmöglichkeiten.

Ziel:  
Nicht sofort auf eine einzelne Feature-Idee festlegen, sondern mehrere mögliche Solutions entwickeln.

Regeln:

- Opportunity und Solution strikt auseinanderhalten.
    
- Für jede Opportunity mehrere alternative Solutions vorschlagen.
    
- Möglichst kleine und einfache Lösungen mit berücksichtigen.
    
- Keine Implementierung und keinen Code erzeugen.
    
- Annahmen jeder Solution nennen.
    

Output:

- Opportunity
    
- mögliche Solutions
    
- jeweilige Annahmen
    
- erwarteter Kundennutzen
    

## 3. critic-validator

Aufgabe:  
Prüfe die vorgeschlagenen Solutions kritisch gegen die vorhandene Customer Evidence und die ursprünglichen Opportunities.

Ziel:  
Erkennen, welche Lösungsideen tatsächlich durch Kundenprobleme gestützt werden und welche hauptsächlich plausible AI-Ideen sind.

Regeln:

- Keine neuen Features erfinden.
    
- Fehlende Evidence ausdrücklich benennen.
    
- Zentrale Annahmen identifizieren.
    
- Vorschlagen, welche Annahmen vor einer Implementierung validiert werden sollten.
    
- Geeignete kleine Experimente oder Nutzertests vorschlagen.
    

Output:

- gestützte Aussagen
    
- ungestützte Annahmen
    
- Risiken
    
- zu validierende Annahmen
    
- mögliche Experimente
    

Erstelle die drei Agent-Dateien und zeige mir anschließend kurz:

1. welche Dateien du angelegt hast,
    
2. welche Aufgabe jeder Agent besitzt,
    
3. welche Tools jeder Agent verwenden darf.
    

Führe die Agenten noch nicht aus.

