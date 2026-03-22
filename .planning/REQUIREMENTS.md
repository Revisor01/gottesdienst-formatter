# Requirements: Gottesdienst-Formatter v2.0

**Defined:** 2026-03-22
**Core Value:** Output muss 1:1 der Boyens-Fließtext-Vorgabe entsprechen — ohne redaktionelle Nacharbeit übernehmbar

## v2.0 Requirements

### Foundation

- [x] **FOUND-01**: App Factory Pattern (create_app()) statt globaler Flask-Instanz
- [x] **FOUND-02**: SQLite-Datenbank mit Flask-SQLAlchemy und Flask-Migrate
- [x] **FOUND-03**: SQLite-Volume in docker-compose.prod.yml für DB-Persistenz
- [x] **FOUND-04**: Persistenter SECRET_KEY (nicht mehr secrets.token_hex Fallback)
- [ ] **FOUND-05**: Health-Check Endpoint /health

### Authentication

- [ ] **AUTH-01**: Login/Logout mit Flask-Login und Session-basierter Auth
- [ ] **AUTH-02**: User-Modell mit Passwort-Hashing (Werkzeug security)
- [ ] **AUTH-03**: Alle bestehenden Routes hinter @login_required
- [ ] **AUTH-04**: Admin-Benutzer kann neue User anlegen und verwalten
- [ ] **AUTH-05**: CSRF-Schutz auf allen Formularen (Flask-WTF)

### UI

- [ ] **UI-01**: Web-Interface Makeover mit Tailwind CSS (Grün als Primärfarbe)
- [ ] **UI-02**: Responsive Layout für Desktop und Tablet
- [ ] **UI-03**: Vorschau des formatierten Textes vor Download mit Warnungen bei Problemen
- [ ] **UI-04**: Excel-Upload-Funktion komplett entfernen (nur noch ChurchDesk-API)

### Settings

- [ ] **SET-01**: Settings-Seite im Web-Interface für User-Konfiguration
- [ ] **SET-02**: Mail-Einstellungen pro User (SMTP-Server, Port, Absender, Empfänger)
- [ ] **SET-03**: Organisationen-Übersicht (welche ChurchDesk-Orgs aktiv sind, aus ENV)
- [ ] **SET-04**: Test-Mail-Button zum Prüfen der SMTP-Konfiguration

### Auto-Mail

- [ ] **MAIL-01**: Automatischer monatlicher E-Mail-Versand des Boyens-Exports
- [ ] **MAIL-02**: Versandzeitpunkt konfigurierbar pro User (Default: 18. des Monats)
- [ ] **MAIL-03**: E-Mail enthält formatierten Text als Anhang (.txt) und im Body
- [ ] **MAIL-04**: APScheduler für zeitgesteuerten Versand (Single-Worker-Constraint)

### Formatierung

- [ ] **FMT-10**: Sonderformat-Titel besser parsen (Gottesdienst mit...: Untertitel → "Gd. m. A." + Untertitel)

## Future Requirements

### Erweiterung
- **EXT-01**: ChurchDesk-Org-Verwaltung in Settings statt nur ENV
- **EXT-02**: Diff-Ansicht zwischen letztem und aktuellem Export

## Out of Scope

| Feature | Reason |
|---------|--------|
| Andere Konfessionen | Kirchenkreis liefert nur ev.-luth. Daten |
| Mobile App | Web-Interface genügt |
| OAuth / Social Login | Flask-Login mit Passwort reicht für internes Tool |
| Celery / Redis | APScheduler in-process genügt für monatlichen Versand |
| PostgreSQL | SQLite reicht für <20 User |
| Flask-Admin | Custom-Routes sind wartbarer als generische Admin-Views |
| Excel-Import | Wird in v2.0 entfernt, nicht verbessert |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 4 | Complete |
| FOUND-02 | Phase 4 | Complete |
| FOUND-03 | Phase 4 | Complete |
| FOUND-04 | Phase 4 | Complete |
| FOUND-05 | Phase 4 | Pending |
| AUTH-01 | Phase 4 | Pending |
| AUTH-02 | Phase 4 | Pending |
| AUTH-03 | Phase 4 | Pending |
| AUTH-04 | Phase 4 | Pending |
| AUTH-05 | Phase 4 | Pending |
| UI-01 | Phase 5 | Pending |
| UI-02 | Phase 5 | Pending |
| UI-03 | Phase 5 | Pending |
| UI-04 | Phase 5 | Pending |
| FMT-10 | Phase 5 | Pending |
| SET-01 | Phase 6 | Pending |
| SET-02 | Phase 6 | Pending |
| SET-03 | Phase 6 | Pending |
| SET-04 | Phase 6 | Pending |
| MAIL-01 | Phase 6 | Pending |
| MAIL-02 | Phase 6 | Pending |
| MAIL-03 | Phase 6 | Pending |
| MAIL-04 | Phase 6 | Pending |

**Coverage:**
- v2.0 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-22*
*Last updated: 2026-03-22 after v2.0 roadmap creation*
