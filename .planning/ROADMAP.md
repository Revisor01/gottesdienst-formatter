# Roadmap: Gottesdienst-Formatter für Boyens Medien

## Overview

Brownfield-Stabilisierung eines funktionierenden, aber technisch verschuldeten Formatierungstools. Der Code läuft — aber dreifach duplizierte Logik, hardcoded API-Tokens und fehlende Tests machen ihn zu fragil für Erweiterungen. Die drei Phasen liefern: saubere Codebasis (Stabilisierung), korrekter Output (Formatierung), automatisierter Betrieb (CI/CD).

Milestone v2.0 baut auf dieser Basis auf und macht aus dem Formatter-Tool eine vollwertige Web-App: Login, Benutzerverwaltung, Settings, automatische Mail, modernes UI.

## Phases

- [x] **Phase 1: Stabilisierung** - Sicherheitslücken schließen und Codebasis bereinigen (Basis für alles Folgende) (completed 2026-03-21)
- [x] **Phase 2: Formatierung** - Output exakt nach Boyens-Vorgabe bringen (Kernzweck des Projekts) (completed 2026-03-21)
- [x] **Phase 3: Pipeline** - Automatisiertes Deployment und Testabdeckung (sicherer Dauerbetrieb) (completed 2026-03-22)
- [x] **Phase 4: Fundament + Auth** - App Factory, Datenbank und Login (Voraussetzung für alle v2.0-Features) (completed 2026-03-22)
- [x] **Phase 5: UI Makeover + Formatierung** - Grünes Interface, Excel-Entfernung und erweitertes Sonderformat-Parsing (completed 2026-03-22)
- [ ] **Phase 6: Settings + Auto-Mail** - User-Einstellungen, SMTP-Versand und automatischer Monatsjob

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
**Goal**: Ein Git-Push loest automatisch Image-Build und Deployment aus — kein manueller Server-Zugriff mehr noetig; Formatierungslogik ist durch Tests abgesichert
**Depends on**: Phase 2
**Requirements**: TEST-01, TEST-02, DEPLOY-01, DEPLOY-02, DEPLOY-03
**Success Criteria** (what must be TRUE):
  1. Ein `git push` auf `main` triggert GitHub Actions, baut ein Docker-Image und pusht es in eine Container Registry (ghcr.io)
  2. Watchtower holt das neue Image automatisch und deployed ohne manuellen `ssh`- oder `docker compose`-Befehl
  3. Formatierungsfunktionen fuer Datum, Zeit, Gottesdienst-Typ und Pastor-Titel haben Unit-Tests — ein Fehler in der Pipeline schlaegt fehl, bevor er auf Produktion geht
  4. Ein Test-Fixture mit echtem Boyens-Referenz-Output existiert und wird als Goldstandard in der CI-Pipeline geprueft
**Plans:** 2/2 plans complete
Plans:
- [x] 03-01-PLAN.md — Unit-Tests und Goldstandard-Fixture fuer Formatierungsfunktionen
- [x] 03-02-PLAN.md — GitHub Actions CI/CD-Pipeline und Produktions-Compose mit Watchtower

### Phase 4: Fundament + Auth
**Goal**: Die App hat eine persistente Datenbank, ein sicheres Login-System und eine saubere Architektur — alle v2.0-Features können auf diesem Fundament aufgebaut werden
**Depends on**: Phase 3
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05, AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05
**Success Criteria** (what must be TRUE):
  1. Benutzer kann sich mit Benutzername und Passwort einloggen und wird nach Logout oder Session-Ablauf auf die Login-Seite umgeleitet
  2. Alle bestehenden Formatter-Seiten sind ohne Login nicht erreichbar — ein direkter URL-Aufruf ohne Cookie leitet auf /login um
  3. Ein Admin-Benutzer kann neue User anlegen und deren Passwörter setzen, ohne Zugriff auf den Server
  4. Die SQLite-Datenbank überlebt ein Watchtower-Redeployment ohne Datenverlust — das Volume ist persistent gemountet
  5. Der Endpunkt /health antwortet mit HTTP 200 und ist ohne Login erreichbar (Docker Healthcheck + Uptime Kuma)
**Plans:** 4/4 plans complete
Plans:
- [x] 04-01-PLAN.md — App Factory, Extensions, User-Modell und Flask-Migrate
- [x] 04-02-PLAN.md — Auth Blueprint: Login/Logout, CSRF, @login_required, /health
- [x] 04-03-PLAN.md — Docker: SQLite Volume, Entrypoint mit Migrationen, Gunicorn
- [x] 04-04-PLAN.md — Admin User-Verwaltung und flask create-admin CLI

### Phase 5: UI Makeover + Formatierung
**Goal**: Die App hat ein modernes, grünes Interface auf Tailwind-Basis, den Excel-Import entfernt und ein verbessertes Sonderformat-Parsing
**Depends on**: Phase 4
**Requirements**: UI-01, UI-02, UI-03, UI-04, FMT-10
**Success Criteria** (what must be TRUE):
  1. Die Benutzeroberfläche zeigt Grün als Primärfarbe und ist auf Desktop und Tablet nutzbar — kein horizontales Scrollen auf einem 768px-Viewport
  2. Der Excel-Upload-Bereich ist nicht mehr sichtbar oder erreichbar — die einzige Datenquelle ist die ChurchDesk-API
  3. Der formatierte Text wird als Vorschau im Browser angezeigt, bevor er heruntergeladen oder kopiert wird; Warnungen bei erkannten Problemen erscheinen sichtbar oberhalb des Textes
  4. Ein Gottesdienst-Titel wie "Gottesdienst mit Abendmahl: Erntedank" erzeugt "Gd. m. A. Erntedank" im Output — Sonderformat und Untertitel werden korrekt kombiniert
**Plans:** 3/3 plans complete
Plans:
- [x] 05-01-PLAN.md — Tailwind CSS CLI Setup, base.html Sidebar-Layout, FMT-10 Sonderformat-Parsing
- [x] 05-02-PLAN.md — Excel-Code entfernen, index.html und result.html Tailwind-Redesign
- [x] 05-03-PLAN.md — churchdesk_events, login und admin Templates Tailwind-Redesign

### Phase 6: Settings + Auto-Mail
**Goal**: Jeder Benutzer kann seinen eigenen SMTP-Versand konfigurieren und Boyens-Exporte werden automatisch monatlich per Mail verschickt
**Depends on**: Phase 5
**Requirements**: SET-01, SET-02, SET-03, SET-04, MAIL-01, MAIL-02, MAIL-03, MAIL-04
**Success Criteria** (what must be TRUE):
  1. Ein eingeloggter Benutzer kann auf einer Settings-Seite SMTP-Server, Port, Absender und Empfänger-Adresse eintragen und mit einem Test-Mail-Button verifizieren, dass die Konfiguration funktioniert
  2. Die Settings-Seite zeigt, welche ChurchDesk-Organisationen aktiv (aus ENV konfiguriert) sind — ohne dass der Benutzer ENV-Variablen kennen muss
  3. Ein Benutzer mit konfiguriertem SMTP empfängt am eingestellten Tag des Monats automatisch eine Mail mit dem formatierten Boyens-Text als .txt-Anhang und im Mail-Body
  4. Ein Benutzer kann den Versandzeitpunkt selbst auf einen anderen Tag des Monats ändern (Default: 18.) — die Änderung greift ab dem nächsten Monat
**Plans:** 2/3 plans executed
Plans:
- [x] 06-01-PLAN.md — UserSettings-Modell, Fernet-Verschluesselung und DB-Migration
- [x] 06-02-PLAN.md — Settings-Blueprint mit Tab-Layout, SMTP-Formular und Test-Mail
- [ ] 06-03-PLAN.md — APScheduler-Integration und automatischer monatlicher Mail-Versand

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Stabilisierung | 3/3 | Complete | 2026-03-21 |
| 2. Formatierung | 2/2 | Complete | 2026-03-21 |
| 3. Pipeline | 2/2 | Complete | 2026-03-22 |
| 4. Fundament + Auth | 4/4 | Complete   | 2026-03-22 |
| 5. UI Makeover + Formatierung | 3/3 | Complete   | 2026-03-22 |
| 6. Settings + Auto-Mail | 2/3 | In Progress|  |
