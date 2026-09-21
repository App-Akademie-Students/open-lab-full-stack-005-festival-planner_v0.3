# Claude Code unter VS Code installieren

Diese Anleitung zeigt Schritt für Schritt, wie **Claude Code** unter **Visual Studio Code** installiert und gestartet wird.

---

## 1. Voraussetzungen

Ihr benötigt:

- **Visual Studio Code 1.98 oder neuer**
- ein **Anthropic-/Claude-Konto**
- eine Internetverbindung

Die installierte VS-Code-Version findet ihr unter:

**Hilfe → Info / About**

---

## 2. VS Code öffnen

Startet **Visual Studio Code**.

Am besten öffnet ihr direkt einen Projektordner:

**Datei → Ordner öffnen**

Zum Beispiel:

```text
festival-planner
```

---

## 3. Erweiterungen öffnen

Öffnet die Extensions-Ansicht mit:

```text
Ctrl + Shift + X
```

Alternativ könnt ihr links in VS Code auf das **Extensions-Symbol** klicken.

---

## 4. Nach Claude Code suchen

Gebt in die Suche ein:

```text
Claude Code
```

Wählt die offizielle Erweiterung:

**Claude Code for VS Code**

Herausgeber:

```text
Anthropic
```

> Achtet darauf, die offizielle Erweiterung von **Anthropic** zu installieren.

---

## 5. Claude Code installieren

Klickt auf:

**Installieren / Install**

Nach der Installation sollte Claude Code in VS Code verfügbar sein.

Falls Claude anschließend nicht angezeigt wird:

```text
Ctrl + Shift + P
```

und ausführen:

```text
Developer: Reload Window
```

Alternativ könnt ihr VS Code neu starten.

---

## 6. Claude Code öffnen

Claude Code kann über die Seitenleiste oder die Command Palette geöffnet werden.

### Variante A: Seitenleiste

Klickt links in VS Code auf das **Claude-Symbol**.

### Variante B: Command Palette

Öffnet:

```text
Ctrl + Shift + P
```

Gebt ein:

```text
Claude Code
```

und wählt zum Beispiel:

```text
Claude Code: Open in New Tab
```

---

## 7. Bei Claude anmelden

Beim ersten Start fordert Claude euch zur Anmeldung auf.

1. Klickt auf **Sign in / Anmelden**
2. Der Browser öffnet sich
3. Meldet euch mit eurem Anthropic-/Claude-Konto an
4. Bestätigt die Verbindung mit VS Code
5. Wechselt zurück zu VS Code

---

## 8. Installation testen

Öffnet einen Projektordner und gebt Claude zum Beispiel folgende Anweisung:

```text
Analysiere dieses Projekt und beschreibe kurz die vorhandene Projektstruktur.
Ändere noch keine Dateien.
```

Claude sollte nun den Projektkontext untersuchen und antworten.

Damit ist die Installation abgeschlossen.

---

# Optional: Claude im VS-Code-Terminal verwenden

Claude Code kann auch direkt im integrierten Terminal verwendet werden.

Öffnet das Terminal:

```text
Ctrl + `
```

und startet Claude mit:

```bash
claude
```

Damit startet Claude Code direkt innerhalb des VS-Code-Terminals.

Eine zusätzliche Installation über npm ist bei Verwendung der aktuellen offiziellen VS-Code-Extension normalerweise nicht notwendig.

---

## Nützliche Claude-Code-Funktionen

Im weiteren Verlauf können unter anderem folgende Funktionen interessant werden.

### Planungsmodus

```text
/plan
```

Claude analysiert zunächst die Aufgabe und erstellt einen Plan, bevor Änderungen vorgenommen werden.

### Projektkontext

Claude kann projektspezifische Anweisungen aus einer Datei namens

```text
CLAUDE.md
```

berücksichtigen.

Darin können zum Beispiel stehen:

- Projektziel
- verwendete Technologien
- Architektur
- Coding-Konventionen
- wichtige Befehle
- Regeln für Claude
- aktuelle Anforderungen

---

# Kurzfassung

```text
1. VS Code öffnen
2. Ctrl + Shift + X
3. Nach "Claude Code" suchen
4. Offizielle Extension von Anthropic installieren
5. Claude Code öffnen
6. Mit Claude-/Anthropic-Konto anmelden
7. Projektordner öffnen
8. Erste Anfrage an Claude stellen
```

---

## Hinweis

Für die Nutzung von Claude Code direkt in VS Code ist die offizielle **Claude-Code-Extension von Anthropic** der einfachste Einstieg.

Eine separate Installation über

```bash
npm install -g @anthropic-ai/claude-code
```

ist für diesen Workshop nicht erforderlich.
