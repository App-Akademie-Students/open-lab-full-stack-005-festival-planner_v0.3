# Neue Features mit AI effizient integrieren

## 1. Continuous Discovery + Opportunity Solution Tree (OST)

*nach Teresa Torres*

### Ansatz

**Continuous Discovery:**
Ein kontinuierlicher Lernprozess über Kundenprobleme, Bedürfnisse und Verhalten.

**Opportunity Solution Tree (OST):**
Die Visualisierung genau dieses Prozesses.

### Kernprinzipien

- **Outcome statt Feature als Ausgangspunkt:** Das Team startet mit einem gewünschten Ergebnis, z. B. „Nutzer planen ihren Festivalbesuch zuverlässiger", nicht mit „Wir bauen eine Favoritenfunktion".
- **Regelmäßiger Kundenkontakt:** Das Produktteam spricht fortlaufend mit Nutzern und sammelt reale Probleme, Wünsche und Verhaltensmuster.
- **Opportunities statt sofort Lösungen:** Aus diesen Erkenntnissen werden Bedürfnisse oder Probleme abgeleitet. Beispiel: „Ich verliere bei mehreren Festivaltagen den Überblick."
- **Mehrere Lösungswege prüfen:** Für eine Opportunity werden verschiedene mögliche Lösungen entwickelt, statt sich sofort auf die erste Feature-Idee festzulegen.
- **Annahmen testen:** Bevor viel entwickelt wird, werden zentrale Annahmen möglichst klein und günstig überprüft.

### Der Opportunity Solution Tree (OST)

Der OST visualisiert genau diesen Prozess:

```
Outcome (das gewünschte Ergebnis)
  ↓
Opportunities
  ↓
Solutions
  ↓
Experiments
```

1. **Outcome** – Welches messbare Ergebnis wollen wir verbessern? Es beschreibt das gewünschte Ziel, nicht bereits eine konkrete Funktion.
2. **Opportunities** – Welche Probleme, Bedürfnisse oder Wünsche der Nutzer stehen diesem Outcome im Weg? Sie werden möglichst aus echtem Kundenfeedback oder Beobachtungen abgeleitet.
3. **Solutions** – Welche unterschiedlichen Lösungen könnten eine Opportunity adressieren? Hier entstehen mögliche Features oder Produktideen.
4. **Experiments** – Wie können wir schnell und mit wenig Aufwand überprüfen, ob eine Solution tatsächlich funktioniert? Zum Beispiel durch Prototypen, Nutzertests oder kleine technische Experimente.

**Kurzform:** Ziel → Problem/Bedürfnis → mögliche Lösung → Überprüfung.

### Beispiel: Festival Planner

```
Outcome
Nutzer können ihren Festivalbesuch besser planen
        ↓
Opportunity
Nutzer verlieren bei mehreren Tagen den Überblick
        ↓
Solutions
├─ Tagesansicht
├─ Filter nach Tag
├─ persönlicher Tagesplan
└─ automatische Planung
        ↓
Experiments
Prototype / Nutzerfeedback / Nutzungsdaten
```

### Der entscheidende Gedanke

**Nicht:**

> Wir haben eine Idee → wir bauen das Feature.

**Sondern:**

> Wir wollen ein Ergebnis verbessern → wir verstehen das Problem → wir betrachten mehrere Lösungen → wir testen → dann bauen wir.

### Was kann die AI davon übernehmen?

Kundenfeedback clustern → Opportunities erkennen → Lösungsalternativen generieren → Annahmen formulieren → Experimente vorschlagen.

---

## 2. Konkretes Beispiel: Festival Planner Features

### Architektur

```
Customer Opportunity Agent
          ↓
Solution Agent
          ↓
Critic / Validation Agent
          ↓
Product Owner (Mensch)
```

```
.claude/
└── agents/
    ├── customer-opportunity.md
    ├── solution-designer.md
    └── critic-validator.md
```

Claude Code unterstützt dieses Modell: Jeder Subagent bekommt einen eigenen System-Prompt, eigene Tools und einen eigenen Kontext. Projektbezogene Agenten liegen unter `.claude/agents/`.

> **Hinweis:** Die `description` eines Claude-Code-Subagents ist wichtig, weil Claude daraus entscheidet, wann es an diesen Agenten delegiert.

### Prompt 1: Subagents anlegen

```
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
```

### Prompt 2: Workflow ausführen

```
Analysiere die Kundenfeedbacks in `teaching/customer-feedback.md`.

Führe dafür die drei vorhandenen Subagents sequenziell aus:

1. `customer-opportunity`
2. `solution-designer`
3. `critic-validator`

Übergib jeweils die relevanten Ergebnisse eines Agents an den nächsten.

Erstelle anschließend eine kompakte Zusammenfassung mit:

- was jeder Agent gemacht hat,
- seinen wichtigsten Ergebnissen,
- der Kette Customer Evidence → Opportunities → Solutions → Validation,
- den offenen Entscheidungen für den Product Owner.

Triff keine Product-Owner-Entscheidung und implementiere noch nichts.
```

### Setup-Reihenfolge (wichtig)

> - aktuelle Claude-Code-Session beenden,
> - im gleichen Projektverzeichnis Claude Code neu starten,
> - prüfen, ob die drei Agenten erkannt werden,
> - erst dann den Workflow-Prompt ausführen.
> - dann Claude fragen: „Welche projektbezogenen Subagents stehen dir zur Verfügung?"

---

## 3. Kundenfeedback (Rohdaten)

1. „Beim Durchsehen des Programms finde ich immer wieder Acts, die mich interessieren. Wenn ich später zurückkomme, muss ich sie aber erneut suchen."
2. „Ich würde interessante Acts gerne mit einem Klick markieren können, damit ich sie beim nächsten Besuch wiedererkenne."
3. „Wenn ich mehrere Acts ausgewählt habe, hätte ich sie gerne direkt zusammen an einer Stelle, ohne das gesamte Programm erneut durchsuchen zu müssen."
4. „Meine ausgewählten Acts sollten möglichst sofort sichtbar sein, wenn ich die Seite öffne."
5. „Die Anwendung funktioniert, wirkt aber noch etwas wie ein technischer Prototyp."
6. „Buttons, Filter und andere Bedienelemente sehen teilweise unterschiedlich aus. Eine einheitlichere Oberfläche würde die Bedienung einfacher machen."
7. „Auf dem Smartphone könnten Abstände, Buttons und Listen besser auf die kleinere Bildschirmgröße abgestimmt sein."
8. „Ich würde mir insgesamt eine modernere und übersichtlichere Oberfläche wünschen, bei der wichtige Aktionen sofort erkennbar sind."

---

## 4. Analyseergebnis der drei Subagents

**Opportunity 1 – Tag/Zeitpunkt-Überblick**
*(Evidence: 2 Zitate – „vergesse Tag" / „verliere Überblick")*

→ **Solutions:** Tages-Gruppierung, Tagesfilter, Merkliste mit Tag/Datum, Kalender-Export

→ **Validator:** Breiteste Evidence-Basis, aber alle 4 Solutions setzen ein aktuell nicht existierendes mehrtägiges Festival voraus (Scope laut `doc/requirements.md`: eintägig) – größtes Risiko: teure Architekturentscheidung ohne Klärung, ob sich das Zitat überhaupt auf das eigene Produkt bezieht.

**Opportunity 2 – Fokussierung auf relevante Bühnen**
*(Evidence: 1 Zitat – „nur zwei Bühnen")*

→ **Solutions:** Filter lokal merken, Mehrfachauswahl, teilbarer Link, Login-Profil

→ **Validator:** Risikoärmste Opportunity – Solution 1 („Filter merken") ist am nächsten an einer kleinen, evidenzgestützten Lösung, da der Bühnenfilter bereits existiert. Solution 4 (Login) widerspricht explizit dem „kein Login"-Scope.

---

## 5. Product-Owner-Entscheidung

> - Acts per Stern als Favoriten markieren.
> - Favoriten lokal persistent speichern.
> - Favoriten oben gesammelt anzeigen.
> - UI moderner und konsistenter gestalten; CSS-Framework prüfen.

**Nächster Schritt:** Change Impact Analysis durchführen und einen minimalen Änderungsplan erstellen. Noch nichts implementieren.
