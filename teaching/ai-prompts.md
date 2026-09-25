# Promts
## 0)


Verschaffe dir bitte zuerst einen Überblick über den aktuellen Stand des Projekts.

1. Prüfe die `CLAUDE.md` auf Konsistenz mit dem aktuellen Projektstand und schlage nötige Anpassungen vor. Noch nichts ändern.
    
2. Was ist bereits umgesetzt?
    
3. Was haben wir zuletzt gemacht?
    
4. Gibt es aktuell offene, uncommittete oder unvollständige Änderungen?
    
5. Welche Aufgaben oder User Stories sind noch offen?
    
6. Was wäre jetzt der sinnvollste nächste Schritt?

## 1. Frontend-Zielbild

Phase 1 – Schritt 1: Baue das Frontend-Zielbild für die semantische Suche.

Ergänze im bestehenden Festival-Planner:

- ein Suchfeld
    
- einen Button „Suchen“
    
- einen Bereich für Suchergebnisse
    
- eine sichtbare Beispielanfrage wie „ruhige elektronische Musik“
    

Verwende zunächst nur Mock-Daten für die Ergebnisse.

Noch keine API-Anbindung, keine Embeddings und keine Vektorsuche implementieren.

Bestehende Funktionen dürfen nicht verändert werden.

## 2. Requirement

Phase 1 – Schritt 2: Ergänze die semantische Suche als Requirement.

Nutzer sollen Acts über natürlich formulierte Suchanfragen finden können.

Die Ergebnisse sollen nach semantischer Ähnlichkeit sortiert werden.

Deutsche Suchanfragen müssen unterstützt werden.

Aktualisiere nur die relevante Requirements-Dokumentation und gegebenenfalls den Projektstatus.

Noch keine Implementierung.

## 3. Suchinhalt festlegen
Phase 1 – Schritt 3: Dokumentiere, welche fachlichen Daten für die semantische Suche verwendet werden.

Entscheidung:

- Durchsucht wird der `Artist`.
    
- Für das Embedding werden `name`, `genre` und `description` verwendet.
    
- `Stage`, `starts_at` und `ends_at` werden nicht in das Embedding aufgenommen.
    
- Diese Informationen werden später über die zugehörigen Acts ergänzt.
    

Noch keine Änderungen am Domain Model, an der Datenbank oder am Anwendungscode vornehmen.


## 4. Domain Model dokumentieren

Phase 1 – Schritt 4: Erweitere die Domain-Model-Dokumentation für die semantische Suche.

`Artist` soll künftig enthalten:

- `name`
    
- `genre`
    
- `description`
    
- `embedding`

## 7. embedding-Spalte technisch anlegen

Phase 1 – Schritt 7: Ergänze die technische Unterstützung für Embeddings im `Artist`-Modell.

Voraussetzungen:

- pgvector ist aktiviert.
    
- Verwendet wird `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
    
- Das Modell liefert 384 Dimensionen.
    

Aufgabe:

- Ergänze `genre` und `description` entsprechend dem geplanten Domain Model, falls sie technisch noch nicht existieren.
    
- Ergänze im SQLAlchemy-Modell `Artist` die Spalte `embedding` vom Typ `vector(384)`.
    
- Verwende die pgvector-Unterstützung für SQLAlchemy.
    
- Passe das Datenbankschema entsprechend an.
    
- `Act` und `Stage` bleiben unverändert.
    
- Setze `EMBEDDING_DIM = 384` zentral, falls eine solche Konstante vorgesehen ist.
    

Noch keine Embeddings erzeugen und noch keine Vektorsuche implementieren.

Führe anschließend die bestehenden Tests aus und aktualisiere die relevante Dokumentation.
