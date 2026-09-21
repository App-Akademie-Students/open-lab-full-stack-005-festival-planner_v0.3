# Roadmap Festival Planner

* Entscheide über Einsatz von AI!
* in welchen Phasen ist AI besonders hilfreich?

1. **Project Goal**
   Wir entwickeln gemeinsam einen kleinen minimalistischen **Festival Planner**.
   User: Wo ist Was Wann?

2. **Backlog anlegen**
   Erste Arbeitspakete sichtbar machen.

3. **Technischen Rahmen festlegen**


4. **Projekt-Setup**
   

5. **Projektkontext / Projektregeln**
   `CLAUDE.md` anlegen und Development Rules definieren.

6. **Anforderungen definieren**
   → [`requirements.md`](requirements.md)

   * Was soll die Anwendung konkret können?
   * Was ist Muss, was ist optional?
   * Welche Benutzeraktionen gibt es?
   * Was gehört bewusst **nicht** zum Scope?

7. **Minimales Domain Model entwerfen**
   → [`domain-model.md`](domain-model.md)
   

8. **Architektur und Projektstruktur festlegen**
   → [`architecture.md`](architecture.md)

9. User Stories ableiten & Backlog konkretisieren
   Backlog verfeinern und erste Features priorisieren.
   → [`backlog.md`](backlog.md)

10. **Implementieren**
    In kleinen Schritten mit Claude.

11. **Testen und Reviewen**

12. **Refactoring / Dokumentation**
    Für v0.1 dokumentiert und freigegeben (siehe [`review.md`](review.md)). Datenbank-Fokus
    wird in Phase 2 (v0.2) unten fortgesetzt.

## Phase 2 – Refactoring v0.2 (Datenbank-Fokus)

Ziel: `Artist`, `Stage`, `Act` als getrennte Entitäten statt einer flachen `ProgramItem`-Tabelle,
bei erhaltener Funktionalität und unveränderter Datenbank (in dieser Phase noch SQLite). Neue
Struktur: `models.py`, `crud.py`, `routers.py`.

13. **Domain Model erweitern**
    → [`domain-model.md`](domain-model.md) – erledigt.

14. **Architektur aktualisieren**
    → [`architecture.md`](architecture.md) – erledigt.

15. **`app/models.py` anlegen**
    `Artist`, `Stage`, `Act` mit Beziehungen – erledigt.

16. **API-Vertrag entscheiden**
    Flache `title`/`stage`-Strings im JSON bleiben (befüllt über die Beziehung) statt
    verschachtelter Objekte – entschieden, siehe `architecture.md`.

17. **`app/seed.py` umstellen**
    Erst `Artist`/`Stage` anlegen, dann `Act` mit FK-Referenzen.

18. **`app/crud.py` einführen**
    Bühnen- und Programm-Query als Funktionen, jetzt mit Joins.

19. **`app/routers.py` einführen**
    Endpunkte aus `main.py` verschieben; `main.py` bindet nur noch den Router ein.

20. **Tests umstellen**
    `tests/test_api.py` auf neue Modelle/Fixtures anpassen.

21. **`app/db.py` auf Infrastruktur reduzieren**
    `ProgramItem` entfernen – erst wenn Schritt 17–20 abgeschlossen sind und nichts mehr
    darauf referenziert.

22. **Testen und Reviewen**
    `python -m pytest` (grün), Review als Nachtrag in [`review.md`](review.md) (Stand
    2026-09-16, Urteil „Freigeben") – erledigt.

## Phase 3 – Umstellung auf PostgreSQL (v0.2)

Ziel: Datenhaltung von der lokalen SQLite-Datei auf eine gehostete PostgreSQL-Datenbank
(Neon) umstellen, bei unveränderter Funktionalität und unverändertem API-Vertrag.
Aufgaben T-10 bis T-14 in [`backlog.md`](backlog.md).

23. **Verbindung konfigurierbar machen**
    `DATABASE_URL` aus `.env` (`python-dotenv`), Engine auf PostgreSQL – erledigt.

24. **Treiber festlegen**
    `psycopg` (v3), `postgresql://` wird in `db.py` auf `postgresql+psycopg://` normalisiert –
    erledigt.

25. **Datenintegrität DB-seitig absichern**
    `ends_at > starts_at` als `CheckConstraint` auf `Act` – erledigt.

26. **Dokumentation nachziehen**
    `requirements.md` (B2, T1), `domain-model.md`, `architecture.md`, `CLAUDE.md`,
    `backlog.md` – erledigt.

27. **Testen und Reviewen**
    `python -m pytest` (läuft weiterhin gegen In-Memory-SQLite) plus lesende Live-Prüfung
    gegen Neon; Review-Nachtrag in [`review.md`](review.md), Abschnitt 7 (Stand 2026-09-18,
    Urteil „Freigeben mit nicht blockierenden Änderungswünschen") – erledigt.

28. **Änderungswünsche aus dem Review umsetzen**
    T-19 (klare Meldung bei fehlender `DATABASE_URL`), T-20 (`pool_pre_ping`) und T-21 (Test
    für die `CheckConstraint`) – erledigt, siehe [`backlog.md`](backlog.md). Die älteren
    Punkte T-15 bis T-18 sind am 2026-09-21 ebenfalls erledigt.





