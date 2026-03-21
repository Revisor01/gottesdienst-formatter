# Roadmap: Gottesdienst-Formatter für Boyens Medien

## Overview

Brownfield-Stabilisierung eines funktionierenden, aber technisch verschuldeten Formatierungstools. Der Code läuft — aber dreifach duplizierte Logik, hardcoded API-Tokens und fehlende Tests machen ihn zu fragil für Erweiterungen. Die drei Phasen liefern: saubere Codebasis (Stabilisierung), korrekter Output (Formatierung), automatisierter Betrieb (CI/CD).

## Phases

- [x] **Phase 1: Stabilisierung** - Sicherheitslücken schließen und Codebasis bereinigen (Basis für alles Folgende) (completed 2026-03-21)
- [ ] **Phase 2: Formatierung** - Output exakt nach Boyens-Vorgabe bringen (Kernzweck des Projekts)
- [ ] **Phase 3: Pipeline** - Automatisiertes Deployment und Testabdeckung (sicherer Dauerbetrieb)

## Phase Details

### Phase 1: Stabilisierung
**Goal**: API-Tokens sind sicher verwahrt, Formatierungslogik ist zentralisiert, neue Kirchengemeinden erfordern keinen Code-Change
**Depends on**: Nothing (first phase)
**Requirements**: SEC-01, SEC-02, CODE-01, CODE-02, CODE-03, CODE-04
**Success Criteria** (what must be TRUE):
  1. Kein API-Token oder Secret Key ist im Quellcode oder Git-History sichtbar — alle Credentials kommen aus Environment Variables
  2. Formatierungslogik (Datum, Zeit, Gottesdienst-Typ, Pastor-Titel) existiert in einem zentralen Modul, das von allen Codepfaden importiert wird
  3. Eine neue ChurchDesk-Organisation wird durch Hinzufügen eines Eintrags in Konfiguration (kein Code-Change) eingebunden
  4. Es gibt eine einzige `format_pastor()`-Funktion — die drei bisherigen Varianten sind entfernt
**Plans:** 3/3 plans complete
Plans:
- [x] 01-01-PLAN.md — Zentrale Module (formatting.py, config.py) erstellen und app.py bereinigen
- [x] 01-02-PLAN.md — Verbleibende Consumer umstellen (churchdesk_api.py, docker-compose, index.html, Standalone-Script)
- [x] 01-03-PLAN.md — Gap Closure: Prototyp loeschen, Token-Rotation dokumentieren

### Phase 2: Formatierung
**Goal**: Der generierte Fließtext ist 1:1 mit der Boyens-Vorgabe — ohne redaktionelle Nacharbeit übernehmbar
**Depends on**: Phase 1
**Requirements**: FMT-01, FMT-02, FMT-03, FMT-04, FMT-05, FMT-06, FMT-07, FMT-08, FMT-09
**Success Criteria** (what must be TRUE):
  1. Ein Export mit bekannten Testdaten produziert exakt den erwarteten Boyens-Fließtext (Datum-Überschrift, Orte alphabetisch, korrekte Abstände)
  2. Zeitangaben erscheinen als "9.30 Uhr" (mit Punkt) und "17 Uhr" (ohne Minuten bei vollen Stunden) — kein anderes Format
  3. Alle Gottesdienst-Typen (Gd., Gd. m. A., Gd. m. T., Familiengd., Konfirmation, Gd. m. Popularmusik, Gd. m. Konfirmandenprüfung) werden korrekt abgekürzt
  4. Alle Pastor-Titel (P., Pn., Diakon, Prädikantin, R.) werden korrekt ausgegeben — mehrere Pastoren pro Gottesdienst durch Komma getrennt
  5. Orte mit mehreren Kirchen zeigen den Kirchennamen (z.B. "Heide, St.-Jürgen"), Orte mit einer Kirche nur den Ortsnamen
**Plans:** 2 plans
Plans:
- [x] 02-01-PLAN.md — Formatierungsfunktionen (format_service_type, format_pastor) auf Boyens-Konformitaet bringen
- [x] 02-02-PLAN.md — Output-Assembly: Ort-Sortierung, Multi-Termin-Zusammenfassung, Location-Extraktion

### Phase 3: Pipeline
**Goal**: Ein Git-Push löst automatisch Image-Build und Deployment aus — kein manueller Server-Zugriff mehr nötig; Formatierungslogik ist durch Tests abgesichert
**Depends on**: Phase 2
**Requirements**: TEST-01, TEST-02, DEPLOY-01, DEPLOY-02, DEPLOY-03
**Success Criteria** (what must be TRUE):
  1. Ein `git push` auf `main` triggert GitHub Actions, baut ein Docker-Image und pusht es in eine Container Registry
  2. Portainer holt das neue Image automatisch und deployt ohne manuellen `ssh`- oder `docker compose`-Befehl
  3. Formatierungsfunktionen für Datum, Zeit, Gottesdienst-Typ und Pastor-Titel haben Unit-Tests — ein Fehler in der Pipeline schlägt fehl, bevor er auf Produktion geht
  4. Ein Test-Fixture mit echtem Boyens-Referenz-Output existiert und wird als Goldstandard in der CI-Pipeline geprüft
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Stabilisierung | 3/3 | Complete   | 2026-03-21 |
| 2. Formatierung | 0/2 | In Progress | - |
| 3. Pipeline | 0/? | Not started | - |
