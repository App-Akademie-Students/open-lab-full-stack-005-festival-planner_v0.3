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

## Technologien

Geplant sind:

* **Python**
* **FastAPI**
* **SQLite**
* **SQLAlchemy**
* **HTML**
* **CSS**
* **JavaScript**
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
├── .gitignore
│
└── doc/
    ├── claude-install.md
    ├── roadmap.md
    ├── requirements.md
    ├── domain-model.md
    ├── architecture.md
    └── backlog.md
```

Die geplante Struktur der Anwendung (`app/`, `static/`, `tests/`) ist in
[`doc/architecture.md`](doc/architecture.md) beschrieben.

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