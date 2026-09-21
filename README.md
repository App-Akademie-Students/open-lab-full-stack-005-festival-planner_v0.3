# Festival Planner

Gemeinsames Open-Lab-Projekt zum Thema:

**Vom Vibe Coding zum Software Engineering**

Ziel ist es, eine kleine Webanwendung strukturiert zu planen und umzusetzen und dabei Claude Code gezielt als Entwicklungswerkzeug einzusetzen.

---

## Ziel des Projekts

Wir entwickeln gemeinsam einen kleinen **Festival Planner**.

Dabei durchlaufen wir typische Schritte der Softwareentwicklung:

* Anforderungen klären
* Projektstruktur festlegen
* Datenmodell entwerfen
* Backend entwickeln
* Frontend entwickeln
* Datenbank anbinden
* testen
* Code überprüfen und verbessern

Claude Code wird dabei unterstützend eingesetzt, zum Beispiel für:

* Anforderungsanalyse
* Projektplanung
* Architekturvorschläge
* Implementierung
* Refactoring
* Tests
* Dokumentation

---

## Aktueller Stand

Umgesetzt sind v0.1, v0.2 und Teile von v0.3: Programm als chronologische Liste, nach Tag
gruppiert, Filter nach Tag und Bühne, Anzeige „läuft jetzt / kommt als Nächstes",
responsive Oberfläche mit Tailwind CSS sowie Favoriten mit persönlichem Zeitplan (nur im
Browser). Die Daten liegen in PostgreSQL bei Neon und werden per Seed-Skript erzeugt.

Details zu Stand, offenen Fragen und nächsten Schritten:
[`doc/project-status.md`](doc/project-status.md). Befehle zum Starten, Seeden und Testen
stehen in [`CLAUDE.md`](CLAUDE.md) unter „Project Commands".

---

## Neue Entwicklungsrichtung: Vektorsuche und LLM

Als Nächstes wird der Festival Planner um eine semantische Suche erweitert – in zwei
getrennten Phasen. Phase 2 beginnt erst, wenn Phase 1 funktioniert und reviewt ist.

**Phase 1 – Semantische Vektorsuche (ohne LLM)**

Ziel: Acts nicht nur über exakte Begriffe finden, sondern nach Bedeutung (z. B.
„ruhige Musik am Abend"). Ergebnis ist eine nach Ähnlichkeit sortierte Liste passender Acts.

```text
Suchanfrage → Embedding-Modell → Query-Vektor → PostgreSQL/pgvector → passende Acts
```

Geplant: durchsuchbare Textfelder im Domain Model festlegen, pgvector in PostgreSQL
aktivieren, Embeddings erzeugen und speichern, Ähnlichkeitssuche im Backend als
FastAPI-Endpunkt bereitstellen und im Frontend einbinden – jeweils mit Tests und Review.

**Phase 2 – LLM / RAG**

Die Treffer aus Phase 1 werden einem LLM als Kontext übergeben, das daraus eine Antwort auf
Fragen in natürlicher Sprache formuliert.

```text
Suchanfrage → Vektorsuche → passende Acts → LLM-Kontext → generierte Antwort
```

Die Vektorsuche bleibt dabei die Retrieval-Schicht; das LLM ersetzt die Datenbanksuche nicht
und darf keine Festivalinformationen erfinden, die nicht in den gefundenen Daten stehen.

**Stand:** Phase 1 ist in Vorbereitung, noch nicht umgesetzt. Phase 2 ist noch nicht begonnen.

---

## Technologien

* **Python**
* **FastAPI** (gestartet über uvicorn)
* **SQLAlchemy**
* **PostgreSQL** (gehostet bei Neon), Treiber `psycopg` – ab Phase 1 zusätzlich **pgvector**
* **HTML**, **Tailwind CSS** (v4, Standalone-CLI)
* **Vanilla JavaScript**
* **pytest** + **httpx** (nur für die Entwicklung)
* **Claude Code**
* **Visual Studio Code**

---

## Voraussetzungen

Ihr benötigt:

* Visual Studio Code
* Python 3
* Git
* Claude Code

Die Installation von Claude Code ist hier beschrieben:

[Claude Code unter VS Code installieren](doc/claude-install.md)

---

## Repository klonen

```bash
git clone https://github.com/App-Akademie-Students/open-lab-full-stack-003-festival-planner.git
```

Anschließend in den Projektordner wechseln:

```bash
cd open-lab-full-stack-003-festival-planner
```

Das Projekt in VS Code öffnen:

```bash
code .
```

---

## Python-Version prüfen

Im Terminal:

```bash
python --version
```

Falls der Befehl unter macOS oder Linux nicht funktioniert:

```bash
python3 --version
```

---

## Virtuelle Python-Umgebung erstellen

Im Hauptverzeichnis des Projekts:

```bash
python -m venv .venv

.venv\Scripts\Activate
```

Unter macOS/Linux gegebenenfalls:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Die virtuelle Umgebung wird im Ordner

```text
.venv
```

angelegt.

---

## Virtuelle Umgebung aktivieren

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Nach erfolgreicher Aktivierung sollte im Terminal ungefähr Folgendes erscheinen:

```text
(.venv)
```

---

## Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

Damit werden alle für das Projekt benötigten Python-Pakete installiert.

---

## Virtuelle Umgebung deaktivieren

Falls ihr die virtuelle Umgebung verlassen möchtet:

```bash
deactivate
```

---

## Claude Code starten

Claude kann direkt über die VS-Code-Erweiterung verwendet werden.

Alternativ im VS-Code-Terminal:

```bash
claude
```

Ein möglicher erster Prompt:

```text
Analysiere das Projekt.

Beschreibe:
- die aktuelle Projektstruktur
- die verwendeten Technologien
- den aktuellen Entwicklungsstand

Ändere noch keine Dateien.
```

---

## CLAUDE.md

Im Projekt befindet sich eine Datei:

```text
CLAUDE.md
```

Sie enthält den zentralen Projektkontext für Claude Code.

Dort können unter anderem festgehalten werden:

* Projektziel
* Technologien
* Architektur
* Coding-Konventionen
* Entwicklungsregeln
* wichtige Befehle
* aktuelle Anforderungen

Die Datei wird während des Projekts gemeinsam weiterentwickelt.

---

## Projektstruktur

Die Projektstruktur wird im Verlauf des Open Labs gemeinsam entwickelt.

Aktueller Stand:

```text
festival-planner/
│
├── README.md
├── CLAUDE.md
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
│
├── app/            # FastAPI-Backend: main, routers, crud, schedule, models, db, seed
├── static/         # Frontend: index.html, app.js, erzeugtes style.css
├── tailwind/       # Tailwind-Quelle input.css
├── tests/          # pytest-Tests
│
└── doc/
    ├── claude-install.md
    ├── roadmap.md
    ├── requirements.md
    ├── requirements-history/
    ├── domain-model.md
    ├── architecture.md
    ├── backlog.md
    ├── review.md
    └── project-status.md
```

Aufgaben der einzelnen Module: [`doc/architecture.md`](doc/architecture.md).

---

## Git

Die virtuelle Python-Umgebung wird nicht in Git gespeichert.

In `.gitignore` sollte deshalb stehen:

```gitignore
.venv/
```

Weitere automatisch erzeugte Dateien können ebenfalls ausgeschlossen werden, zum Beispiel:

```gitignore
__pycache__/
*.pyc
```

---

## Open Lab

Das Projekt wird gemeinsam in mehreren Sessions entwickelt.

Der Fokus liegt nicht nur darauf, dass die Anwendung funktioniert.

Wir wollen nachvollziehen, wie aus einer zunächst einfachen Idee Schritt für Schritt ein strukturiertes Softwareprojekt entsteht:

**Idee → Anforderungen → Planung → Architektur → Implementierung → Tests → Verbesserung**

Dabei untersuchen wir insbesondere, an welchen Stellen AI-Unterstützung hilfreich ist und wo weiterhin Software-Engineering-Entscheidungen notwendig sind.

## Claude Artifact
[Claude Artifact](https://claude.ai/artifact/NQw23WBkEX6NShoPfbbmfq)