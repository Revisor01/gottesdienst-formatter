# Feature Research

**Domain:** Internal Flask web tool — church service formatter with auth, settings, auto-email
**Researched:** 2026-03-22
**Confidence:** HIGH (Flask ecosystem well-documented, patterns well-established)

## Feature Landscape

### Table Stakes (Users Expect These)

Features Nutzer erwarten. Fehlen sie, wirkt das Produkt unfertig.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Login / Session-Auth | Zugang zu einem Multi-User-Tool braucht Authentifizierung | LOW | Flask-Login, @login_required Decorator, Werkzeug password_hash — Standardbibliothek |
| Logout | Jede Auth-implementierung braucht sauberes Session-Ende | LOW | Flask-Login logout_user(), Session-Cookie löschen |
| Passwort-Hashing | Plaintext-Passwörter = kein echtes Auth | LOW | Werkzeug bereits in requirements.txt — generate_password_hash / check_password_hash |
| "Falsche Zugangsdaten" ohne Detail-Leak | Kein Hinweis ob Username oder Passwort falsch | LOW | Einheitliche Fehlermeldung "Ungültige Zugangsdaten" |
| Redirect nach Login | Nutzer landen nach Login dort, wo sie hinwollten | LOW | Flask-Login next-Parameter |
| Settings-Seite pro User | Konfiguration (Mail, Orgs) muss editierbar sein, nicht per ENV | MEDIUM | Eigene Route /settings, User-Objekt mit Konfigurations-Feldern in DB |
| Datenbankpersistenz für User + Settings | Ohne DB: keine User-Verwaltung, keine Settings | MEDIUM | Flask-SQLAlchemy + SQLite reicht für diese Nutzerzahl (<20 User) |
| Health-Check Endpoint | Docker und Uptime-Kuma erwarten /health oder /ping | LOW | Minimalroute, gibt JSON {"status": "ok"} zurück, kein Auth nötig |
| CSRF-Schutz bei Forms | Standard-Sicherheitsanforderung bei POST-Formularen | LOW | Flask-WTF (WTForms), bereits gut etabliert im Flask-Ökosystem |

### Differentiators (Competitive Advantage)

Features, die dieses Tool von einem generischen Formatter abheben.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Auto-E-Mail an Boyens | Kernwert: kein manuelles Kopieren + Mailen — per Knopfdruck direkt abschicken | MEDIUM | Flask-Mail + SMTP-Konfiguration pro User in DB; SMTP-Credentials verschlüsselt speichern oder via App-Secret ableiten |
| Mail-Einstellungen pro User (nicht ENV) | Verschiedene Pastoren können verschiedene Absenderadressen nutzen | MEDIUM | User-Model bekommt Felder smtp_host, smtp_user, smtp_password, recipient_email; Settings-Seite rendert Formular |
| Vorschau mit Warnungen | Nutzer sieht Format-Output + potenzielle Probleme VOR dem Senden | MEDIUM | Render-Preview im Template, Warnungen als Liste (z.B. "Kein Pastor angegeben für Bredstedt", "Unbekannter Standort") |
| Sonderformat-Titel-Parsing | Gottesdienst-Sondertypen korrekt erkennen und formatieren (aktuell unvollständig) | MEDIUM | Erweiterung in formatting.py — pattern-matching auf Titel-Strings, Regression-Tests gegen Goldstandard-Fixture |
| Admin-Panel für User-Verwaltung | Ein Admin-Nutzer kann weitere Accounts anlegen / deaktivieren | MEDIUM | Eigene /admin/users Route, is_admin-Flag auf User-Modell, @admin_required Decorator |
| Excel-Import-Entfernung | Vereinfacht UI erheblich — nur noch ChurchDesk-Flow | LOW | Routen /upload und process_excel_file() löschen, Templates bereinigen |
| UI-Makeover (grün) | Klare Markenidentität, modernes Erscheinungsbild | LOW-MEDIUM | Tailwind CSS oder einfaches Custom CSS; Grün ist gesetzt als Farbe |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| OAuth / SSO (Google, Microsoft) | "Moderner" Login ohne Passwörter | Komplexität (flask-authlib, Callback-URLs, Token-Refresh) unverhältnismäßig für <20 interne User | Flask-Login mit eigenem Passwort-Hash — simpel, wartbar |
| Passwort-Reset per E-Mail | Nutzer erwarten "Passwort vergessen"-Link | Braucht eigenes Token-System, SMTP-Konfiguration muss funktionieren bevor User einloggt — Henne-Ei-Problem | Admin setzt Passwort manuell zurück über Admin-Panel |
| Zwei-Faktor-Authentifizierung (2FA) | Erhöhte Sicherheit | Für ein internes Tool mit <20 Nutzern unverhältnismäßig | Starke Passwörter, HTTPS bereits gegeben |
| Audit-Log / Aktivitätsverlauf | "Wer hat was gemacht?" | Erheblich mehr DB-Schema, UI; bringt keinen unmittelbaren Wert | Nicht bauen — Anforderung nicht gestellt |
| Rollenbasiertes Berechtigungssystem (RBAC) | Feinere Kontrolle | Überdimensioniert: es gibt nur "Admin" und "User" — zwei Levels reichen | Boolean is_admin auf User-Modell |
| Asynchrones E-Mail-Versenden (Celery/Redis) | Kein Timeout bei langem SMTP | Celery + Redis erhöht Infrastruktur-Komplexität massiv | SMTP mit Timeout-Parameter, Flask-Mail verbindet synchron — völlig ausreichend für ein Mail pro Export-Aktion |
| Vollständige Flask-Admin Integration | Fertige Admin-UI | Flask-Admin generiert generische CRUD-Views, passt nicht gut zu Custom-Workflow | Eigene /admin/users Route — 30 Zeilen Code, volle Kontrolle |

## Feature Dependencies

```
[Datenbank (SQLAlchemy + SQLite)]
    └──requires──> [User-Modell]
                       ├──requires──> [Login / Session-Auth]
                       │                  └──requires──> [Alle anderen Routes mit @login_required]
                       ├──requires──> [Settings-Seite]
                       │                  └──enables──> [Auto-E-Mail an Boyens]
                       └──requires──> [Admin-Panel User-Verwaltung]

[Vorschau mit Warnungen]
    └──requires──> [ChurchDesk-API-Fetch] (bereits vorhanden)
    └──enhances──> [Auto-E-Mail an Boyens] (Preview vor dem Senden)

[Sonderformat-Titel-Parsing]
    └──enhances──> [Vorschau mit Warnungen] (mehr erkannte Typen = weniger Warnungen)

[Excel-Import-Entfernung]
    └──conflicts──> [nichts] (isolierte Bereinigung, keine Abhängigkeit)

[UI-Makeover]
    └──unabhängig──> [alle anderen Features] (kann parallel oder zum Schluss)

[Health-Check Endpoint]
    └──unabhängig──> [alle anderen Features] (drei Zeilen, jederzeit ergänzbar)
```

### Dependency Notes

- **Datenbank requires User-Modell:** Ohne DB-Schema kein persistentes Auth-System. SQLAlchemy-Modelle sind Basis für alles Weitere.
- **Login requires Datenbank:** Flask-Login braucht ein User-Loader-Callback, das aus der DB lädt. Ohne DB kein Login.
- **Settings-Seite requires User-Modell:** SMTP-Credentials und Org-Auswahl werden am User-Objekt gespeichert — kein separates Config-Modell nötig.
- **Auto-E-Mail requires Settings-Seite:** SMTP-Konfiguration muss existieren, bevor E-Mail ausgelöst werden kann. Ohne konfigurierte Einstellungen: Warnung anzeigen statt Absturz.
- **Vorschau enhances Auto-E-Mail:** Logisch sinnvoll als Zwischenschritt — Preview zeigen, dann senden. Kein technisches Muss, aber gute UX.
- **Excel-Entfernung conflicts mit nichts:** Isolierter Abbau. Kann in eigenem Commit/Phase erfolgen ohne andere Features zu blockieren.

## MVP Definition

### Launch With (v2.0)

Minimum für den Relaunch als echte App.

- [ ] Datenbank-Setup (SQLAlchemy + SQLite, User-Modell) — Basis für alles
- [ ] Login / Logout / @login_required auf allen Routen — Multi-User-Schutz
- [ ] CSRF-Schutz (Flask-WTF) — Sicherheits-Baseline
- [ ] Settings-Seite pro User (SMTP, Empfänger-Mail) — ohne das kein Auto-Mail
- [ ] Auto-E-Mail an Boyens (Flask-Mail, per Knopf aus Result-Seite) — Kernmehrwert v2.0
- [ ] Admin-Panel User-Verwaltung (User anlegen, Passwort setzen, is_admin) — Betrieb ohne Zugriff auf Server
- [ ] Excel-Import entfernen — UI-Bereinigung
- [ ] UI-Makeover (grün) — gesetzt als Anforderung
- [ ] Health-Check Endpoint /health — Docker + Uptime-Kuma

### Add After Validation (v2.x)

Nach erfolgreichem v2.0-Rollout.

- [ ] Vorschau mit Warnungen — erhöht Vertrauen in Output, aber kein Blocker für Launch
- [ ] Sonderformat-Titel-Parsing-Erweiterung — Qualitätsverbesserung, iterativ ergänzbar
- [ ] Passwort-Änderung durch User selbst (ohne Admin) — Komfort-Feature

### Future Consideration (v3+)

Nicht in v2.0, kein konkreter Bedarf belegt.

- [ ] E-Mail-Versandhistorie — wer hat wann an Boyens geschickt
- [ ] Mehrere Empfänger pro User
- [ ] Vorlagen-Verwaltung für Sonderformate

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Login / Session-Auth | HIGH | LOW | P1 |
| Datenbank (SQLAlchemy + SQLite) | HIGH | LOW | P1 |
| CSRF-Schutz | HIGH | LOW | P1 |
| Settings-Seite | HIGH | MEDIUM | P1 |
| Auto-E-Mail an Boyens | HIGH | MEDIUM | P1 |
| Admin-Panel User-Verwaltung | HIGH | MEDIUM | P1 |
| Excel-Import-Entfernung | MEDIUM | LOW | P1 |
| Health-Check Endpoint | MEDIUM | LOW | P1 |
| UI-Makeover (grün) | MEDIUM | MEDIUM | P1 |
| Vorschau mit Warnungen | HIGH | MEDIUM | P2 |
| Sonderformat-Titel-Parsing | MEDIUM | MEDIUM | P2 |
| Passwort-Änderung durch User | LOW | LOW | P2 |
| E-Mail-Versandhistorie | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Muss für v2.0-Launch
- P2: Sollte ergänzt werden, wenn P1 stabil
- P3: Nice-to-have, kein konkreter Bedarf

## Competitor Feature Analysis

Kein direkter Wettbewerb (internes Tool), aber vergleichbare interne Tools:

| Feature | Typisches internes Tool | Unser Ansatz |
|---------|------------------------|--------------|
| Auth | Kein Auth oder HTTP Basic Auth | Flask-Login mit DB-backed User-Modell |
| E-Mail | Manuell kopieren + senden | Auto-Mail direkt aus der App |
| Konfiguration | ENV-Variablen | Settings-Seite pro User in DB |
| Admin | Direkt DB-Zugriff oder kein Admin | Einfaches Admin-Panel in der App |
| Vorschau | Ergebnis ohne Kontext | Vorschau + Warnungen vor dem Senden |

## Sources

- [Flask-Login 0.7.0 Documentation](https://flask-login.readthedocs.io/)
- [Flask Security Best Practices 2025 (Corgea)](https://hub.corgea.com/articles/flask-security-best-practices-2025)
- [Flask-Admin Documentation](https://flask-admin.readthedocs.io/en/latest/introduction/)
- [Flask-Admin GitHub (pallets-eco)](https://github.com/pallets-eco/flask-admin)
- [Flask-Mail / Mailtrap Guide 2026](https://mailtrap.io/blog/flask-email-sending/)
- [Flask Health Check Best Practices](https://dev-radar.com/articles/2023/06/21/best-practices-for-implementing-a-health-check-endpoint-in-flask-api/)
- [Flask SQLAlchemy Documentation](https://flask-sqlalchemy.readthedocs.io/en/stable/)
- [Flask WTForms Pattern](https://flask.palletsprojects.com/en/stable/patterns/wtforms/)

---
*Feature research for: Gottesdienst-Formatter v2.0 — Flask internal tool*
*Researched: 2026-03-22*
