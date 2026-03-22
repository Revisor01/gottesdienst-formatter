# Pitfalls Research

**Domain:** Flask App Erweiterung — Auth, DB, Scheduled Tasks, UI Overhaul
**Researched:** 2026-03-22
**Confidence:** HIGH (projektspezifisch, basierend auf Codebasis-Analyse + bekannten Flask-Patterns)

---

## Critical Pitfalls

### Pitfall 1: Secret Key regeneriert sich bei jedem Container-Neustart — alle Sessions werden ungültig

**What goes wrong:**
`app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)` — der Fallback generiert bei jedem Start einen neuen Key. Mit Watchtower (automatisches Redeployment) werden alle eingeloggten User bei jedem Deploy ausgeloggt. Flask-Login Sessions sind Cookie-basiert, verschlüsselt mit dem Secret Key.

**Why it happens:**
Der Fallback war für Entwicklung gedacht. Ohne Login war es egal. Mit Login ist ein stabiler, persistenter Key Pflicht.

**How to avoid:**
`SECRET_KEY` muss immer in den Docker-ENV-Vars gesetzt sein — kein Fallback. Beim Setup-Check verifizieren: `if not os.getenv('SECRET_KEY'): raise RuntimeError("SECRET_KEY not set")`. Den Key einmalig mit `secrets.token_hex(32)` generieren und dauerhaft in `.env` auf dem Server hinterlegen.

**Warning signs:**
- User werden nach Container-Restart ausgeloggt
- Session-Cookies funktionieren nicht nach neuem Deploy

**Phase to address:**
Phase "Datenbank + Auth Foundation" — als erster Schritt vor Flask-Login-Integration.

---

### Pitfall 2: Datenbankmigrationen mit Watchtower — `db.create_all()` vs. Alembic

**What goes wrong:**
`db.create_all()` erstellt Tabellen nur, wenn sie nicht existieren. Es aktualisiert keine bestehenden Tabellen (neue Spalten, geänderte Typen). Bei Watchtower-Auto-Deployment wird der Container getauscht, aber die SQLite-Datei bleibt. Nach Schema-Änderungen (z.B. neue Spalte in `User`) startet die App, `create_all()` macht nichts, und der Code greift auf eine Spalte zu, die nicht existiert — `OperationalError`.

**Why it happens:**
Entwickler verwenden `db.create_all()` für den ersten Start, vergessen aber, dass spätere Deploys mit existierender DB laufen. Watchtower macht das unsichtbar — der Container startet einfach neu.

**How to avoid:**
Flask-Migrate (Alembic) von Anfang an einsetzen. Migration-Skripte ins Repo commiten. Im Container-Entrypoint `flask db upgrade` vor dem App-Start ausführen — nicht `db.create_all()`. Die SQLite-Datei als Docker-Volume persistent mounten (z.B. `./data:/app/data`).

**Warning signs:**
- `OperationalError: no such column` nach einem Deploy
- App startet, aber Login-Seite gibt 500er

**Phase to address:**
Phase "Datenbank + Auth Foundation" — Migrations-Setup als Teil der DB-Initialisierung.

---

### Pitfall 3: Bestehende Routes ohne `@login_required` — partielle Auth-Abdeckung

**What goes wrong:**
`/fetch_churchdesk_events` und `/export_selected_events` werden vergessen oder bewusst "erstmal offen gelassen". Ergebnis: UI zeigt Login, aber die eigentliche Funktionalität ist ohne Auth erreichbar — ChurchDesk-Tokens im Klartext nutzbar von Unbefugten.

**Why it happens:**
Man schützt zuerst nur die neue Settings-Seite. Die bestehenden Routes sehen "erstmal unwichtig" aus, weil sie keine neuen Features haben. Aber sie beinhalten API-Token-Zugriff.

**How to avoid:**
Auth als eine atomare Änderung: In einer Phase alle Routes auf `@login_required` umstellen. Keine Route "später" schützen. Explizite Whitelist für öffentliche Routes (nur `/login`, `/health`).

**Warning signs:**
- `/fetch_churchdesk_events` antwortet mit 200 ohne Cookie

**Phase to address:**
Phase "Datenbank + Auth Foundation" — Login-Integration bedeutet: alle Routes schützen, nicht nur neue.

---

### Pitfall 4: SQLite-Datei im Container-Filesystem — Datenverlust bei Watchtower-Deploy

**What goes wrong:**
SQLite-Datei liegt standardmäßig im Container-Verzeichnis. Watchtower tauscht den Container aus (altes Image weg, neues Image rein). Alle User-Accounts und Settings sind weg. Die App startet leer.

**Why it happens:**
Das aktuelle `docker-compose.yml` hat nur `./uploads:/app/uploads` als Volume. SQLite würde analog vergessen werden.

**How to avoid:**
Volume für die Datenbank explizit definieren: `./data:/app/data`. `DATABASE_URL` auf diesen Pfad zeigen. Im `docker-compose.yml` sicherstellen, dass `data/` auf dem Host-Server angelegt wird bevor der erste Start.

**Warning signs:**
- Nach Deploy sind alle User weg
- App zeigt keine konfigurierten Organisationen

**Phase to address:**
Phase "Datenbank + Auth Foundation" — Volume-Konfiguration im docker-compose.yml.

---

### Pitfall 5: APScheduler in Docker — Scheduled Tasks laufen doppelt oder gar nicht

**What goes wrong:**
APScheduler wird direkt in der Flask-App initialisiert. Mit Flask im Debug-Mode oder mit Gunicorn Multi-Worker läuft der Scheduler in mehreren Prozessen gleichzeitig — E-Mail wird 2-4x verschickt. Im Docker-Container mit einem Worker: kann durch den `start_scheduler()` Aufruf beim Import doppelt starten (Flask Reloader).

**Why it happens:**
`scheduler.start()` im globalen App-Scope wird bei jedem Worker-Start ausgeführt. Gunicorn mit `--workers 2` = 2 Scheduler-Instanzen = 2 E-Mails.

**How to avoid:**
Gunicorn in Production auf 1 Worker beschränken (akzeptabel für diese App-Größe). Oder: separater Celery-Worker, aber das ist Overengineering für diesen Use Case. APScheduler mit `replace_existing=True` und Job-Store konfigurieren. Alternativ: systemd-Timer oder Cron-Job außerhalb des Containers, der einen HTTP-Endpoint triggert.

**Warning signs:**
- Boyens erhält E-Mail mehrfach
- Log zeigt mehrfaches "Scheduler gestartet"

**Phase to address:**
Phase "Automatische E-Mail" — Scheduler-Initialisierung explizit mit Single-Worker-Constraint.

---

### Pitfall 6: Mail-Settings in DB aber ChurchDesk-Tokens noch in ENV — inkonsistente Konfigurationsquellen

**What goes wrong:**
Mail-Einstellungen werden in der DB gespeichert (pro User). ChurchDesk-Tokens bleiben in ENV-Vars (aktuelles Design). Der Scheduled Task für automatische E-Mail muss beide Quellen kombinieren: DB für Mail-Config, ENV für API-Tokens. Wenn ENV-Vars beim Deploy fehlen, schlägt der Task lautlos fehl oder crasht.

**Why it happens:**
Die Entscheidung "Mail-Config in DB, Tokens in ENV" ist richtig, aber der Scheduled Task muss beide Quellen kennen. Fehlerbehandlung beim Laden der ENV-Konfiguration wird vergessen.

**How to avoid:**
Health-Check-Endpoint (`/health`) muss prüfen: DB erreichbar + mindestens ein Org-Token konfiguriert + SMTP-Config vorhanden. Scheduled Task immer mit explizitem Try/Except und Logging — kein silenter Fehler. Beim Task-Start Konfiguration validieren, nicht erst beim Senden.

**Warning signs:**
- `/health` gibt 200, aber E-Mail kommt nicht an
- Kein Fehlerlog trotz ausbleibendem E-Mail-Versand

**Phase to address:**
Phase "Automatische E-Mail" — Health-Check als Teil der Task-Implementation.

---

### Pitfall 7: UI-Makeover bricht bestehende JavaScript-Logik (Events JSON / Clipboard)

**What goes wrong:**
`churchdesk_events.html` enthält JavaScript, das auf spezifische HTML-Elemente mit bestimmten IDs/Klassen wartet (Checkbox-Handling, `events_json` Hidden-Field, Clipboard-Funktion). Ein Template-Makeover, der IDs umbenennt oder die DOM-Struktur ändert, bricht das JS lautlos — kein Fehler, aber Checkboxen haben keine Wirkung.

**Why it happens:**
Designer/Entwickler sieht Templates als rein visuell. JS-Abhängigkeiten sind nicht dokumentiert. Kein automatischer Test für Frontend-Interaktion.

**How to avoid:**
Vor dem UI-Makeover: alle JS-abhängigen Element-IDs und -Klassen dokumentieren (z.B. `#events-form`, `#formatted-output`, `[name="selected_events"]`). Diese als "API" behandeln — können nur absichtlich umbenannt werden. Nach Makeover: manueller Test des kompletten Workflows (ChurchDesk-Events fetchen → auswählen → exportieren → Clipboard).

**Warning signs:**
- Checkboxen auswählen hat keinen Effekt auf Export
- Clipboard-Button kopiert leeren String

**Phase to address:**
Phase "UI Makeover" — Checkliste mit JS-Abhängigkeiten vor Beginn anlegen.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `db.create_all()` statt Flask-Migrate | Kein Setup-Aufwand | Schema-Änderungen erfordern manuelles DB-Eingreifen oder Datenverlust | Nur für throw-away Prototypen, nie in Production mit Watchtower |
| Passwörter als SHA256-Hash | Einfach zu implementieren | Unsicher, kein Salt — Regenbogentabellen-Angriff | Nie — immer bcrypt/werkzeug.security |
| Sessions für Mail-Config-Cache | Kein DB-Query pro Request | Sessions sind client-seitig, Config-Änderungen greifen erst nach Re-Login | Nie für Security-relevante Daten |
| Scheduled Task im Flask-App-Prozess | Keine separate Infrastruktur | Doppelter Versand bei Multi-Worker, keine Retry-Logik | Akzeptabel bei Single-Worker + explizitem Constraint |
| Globale `ORGANIZATIONS` aus ENV laden | Kein DB-Setup nötig | Org-Konfiguration ist in Settings nicht editierbar — muss für v2.0 aus DB kommen | Nur in v1.x, muss in v2.0 refactored werden |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Flask-Login + bestehende Routes | `current_user` in Templates nutzen bevor `login_manager.user_loader` korrekt konfiguriert ist → `AttributeError` | `user_loader` als erstes implementieren, dann Templates anpassen |
| Flask-Migrate + SQLite | `flask db init` im Container ohne gemounteten Volume → Migrations-Ordner geht bei Deploy verloren | `migrations/`-Ordner ins Git-Repo commiten, nicht im Container erstellen |
| APScheduler + Flask App Context | `db.session` im Task ohne App Context → `RuntimeError: Working outside of application context` | Tasks immer mit `with app.app_context():` wrappen |
| SMTP + Docker | SMTP-Credentials in DB, aber kein Test-Endpoint → User weiß nicht ob Config korrekt ist | "Test-Mail senden"-Button in Settings implementieren |
| Watchtower + ENV-Vars | Neues ENV-Var im Code, aber nicht in `.env` auf Server → Container startet, aber Feature fehlt lautlos | Startup-Validierung aller Required ENV-Vars |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| ChurchDesk-API-Call beim Login | Jede geschützte Route triggert API-Call zur Validierung | API-Calls nur on-demand, nie in Auth-Middleware | Ab erstem Nutzer |
| DB-Query für ORGANIZATIONS bei jedem Request | Wenn Org-Config aus DB kommt: globale `ORGANIZATIONS` wird nicht mehr gecacht | `functools.lru_cache` oder App-Start-Cache für Org-Config | Kein echtes Scale-Problem, aber unnötige DB-Latenz |
| Kein Connection-Pooling für SQLite | SQLite ist file-based, aber bei concurrent Requests kann es zu Lock-Errors kommen | `check_same_thread=False` in SQLAlchemy + WAL-Mode für SQLite | Bei >2 gleichzeitigen Usern |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| ChurchDesk-API-Tokens im Browser-zugänglichen Response | Tokens in `events_json` landen im HTML — aktuell sichtbar im Page-Source | Tokens niemals in Client-seitiges JSON — nur Event-IDs übergeben |
| Passwort-Reset ohne Rate-Limiting | Brute-Force auf Login-Endpoint | Flask-Limiter für `/login`-Route (z.B. 10 Versuche/Minute) |
| SMTP-Passwort in DB im Klartext | Bei DB-Dump kompromittiert | Verschlüsselung mit Fernet (symmetrisch, Key aus SECRET_KEY ableiten) oder zumindest dokumentieren dass Risiko bekannt ist |
| Admin-Funktionen nur durch `is_admin`-Flag ohne Route-Check | Flag in DB änderbar wenn SQLite-Datei kompromittiert | `is_admin`-Dekorator konsequent auf allen Admin-Routes |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Login-Redirect verliert gewählten Monat/Jahr | User wählt März 2026, wird zu Login weitergeleitet, kommt danach auf Startseite — muss Monat neu wählen | `next`-Parameter in Login-URL mitgeben und nach Login nutzen |
| Settings-Seite speichert ohne Bestätigung | User ändert Mail-Adresse versehentlich | Explizites "Speichern"-Submit + Success-Flash-Message |
| Kein visuelles Feedback beim automatischen E-Mail-Versand | User weiß nicht ob E-Mail gesendet wurde | Versand-Log in DB speichern, in UI anzeigen ("Letzte E-Mail: 15. März 2026, 08:00") |
| Export-Button nach Login noch sichtbar aber nicht funktional | Wenn Auth-Fehler im Hintergrund passiert, sieht User leere Ausgabe | 401-Responses immer mit Redirect zum Login, nie stilles Scheitern |

---

## "Looks Done But Isn't" Checklist

- [ ] **Login:** Funktioniert im Browser, aber `@login_required` fehlt auf `/fetch_churchdesk_events` und `/export_selected_events` — manuell testen ohne Cookie
- [ ] **Datenbankmigrationen:** `flask db upgrade` läuft lokal, aber im Container-Entrypoint nicht eingebaut — nach Watchtower-Deploy Schema-Check
- [ ] **Automatische E-Mail:** Scheduler startet laut Log, aber sendet nicht — App-Context-Wrapper im Task vergessen
- [ ] **Settings speichern:** Formular POST gibt 200, aber DB wurde nicht geschrieben — fehlende `db.session.commit()`
- [ ] **SQLite-Volume:** Container läuft, DB existiert, aber bei `docker compose down && up` ist DB weg — Volume-Mount im docker-compose.yml überprüfen
- [ ] **SECRET_KEY:** App läuft ohne gesetzten Key (Fallback greift), aber nach Neustart sind alle Sessions ungültig — Startup-Check hinzufügen
- [ ] **UI-Makeover:** Alle Seiten sehen gut aus, aber Clipboard funktioniert nicht — JS-Element-IDs nach Makeover prüfen

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| SQLite-Datenverlust (kein Volume) | HIGH | Neues Volume anlegen, alle User neu anlegen, Settings neu konfigurieren — kein Backup möglich wenn es nie gemountet war |
| Schema-Mismatch nach Deploy | MEDIUM | `docker exec` in Container, `flask db upgrade` manuell ausführen; bei Fehler: DB-Dump, Schema-Fix, Import |
| Scheduler sendet doppelt | LOW | Gunicorn-Worker auf 1 reduzieren, Container neustarten |
| Sessions nach Deploy ungültig | LOW | User müssen sich neu einloggen — kein Datenverlust, aber frustrierend; SECRET_KEY persistent setzen |
| JS-Funktionalität nach UI-Makeover defekt | MEDIUM | Element-IDs im JS identifizieren, in Templates wiederherstellen; 1-2h Debugging ohne Dokumentation |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| SECRET_KEY Fallback | Phase 1: DB + Auth Foundation | `docker compose down && up` — Login bleibt erhalten |
| DB-Migrationsfehler mit Watchtower | Phase 1: DB + Auth Foundation | Schema-Änderung deployen ohne manuellen DB-Eingriff |
| SQLite-Volume fehlt | Phase 1: DB + Auth Foundation | `docker compose down && up` — User-Account bleibt erhalten |
| Ungeschützte Routes | Phase 1: DB + Auth Foundation | `curl` ohne Cookie auf `/fetch_churchdesk_events` gibt 302 |
| Scheduler doppelter Versand | Phase 3: Automatische E-Mail | Gunicorn-Worker-Anzahl im Dockerfile/compose dokumentiert |
| APScheduler ohne App Context | Phase 3: Automatische E-Mail | Task läuft durch ohne RuntimeError im Log |
| Mail-Config-Validierung | Phase 3: Automatische E-Mail | `/health` schlägt fehl wenn SMTP nicht konfiguriert |
| JS-Abhängigkeiten nach Makeover | Phase 2: UI Makeover | End-to-End-Test: ChurchDesk → Auswahl → Export → Clipboard |
| Login-Redirect verliert State | Phase 1: DB + Auth Foundation | Nach Login mit `?next=...` landet User auf gewünschter Seite |

---

## Sources

- Codebasis-Analyse: `/Users/simonluthe/Documents/kk-termine/web/app.py`, `config.py`, `docker-compose.yml`
- Flask-Login Dokumentation: https://flask-login.readthedocs.io/en/latest/
- Flask-Migrate (Alembic): https://flask-migrate.readthedocs.io/en/latest/
- APScheduler Flask-Integration: https://apscheduler.readthedocs.io/en/3.x/userguide.html
- Bekanntes Pattern: Watchtower + SQLite Volume (Community-Erfahrung, HIGH confidence)
- Projektkontext: `.planning/PROJECT.md`

---
*Pitfalls research for: Flask App Erweiterung — Auth, DB, Scheduled Tasks, UI Overhaul*
*Researched: 2026-03-22*
