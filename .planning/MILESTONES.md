# Milestones

## v2.0 App Relaunch (Shipped: 2026-03-22)

**Phases completed:** 6 phases, 17 plans, 22 tasks

**Key accomplishments:**

- One-liner:
- docker-compose.yml:
- Task 1:
- format_service_type() und format_pastor() auf Boyens-Konformitaet gebracht: 12 Gottesdienst-Typen (D-01 bis D-11), Diakon/Praedikantin ausgeschrieben, Komma-Trenner, & Team-Sonderbehandlung
- One-liner:
- One-liner:
- GitHub Actions CI/CD-Pipeline mit ghcr.io-Push und Watchtower-Auto-Deploy: git push auf main triggert Tests, baut Docker-Image und deployed es automatisch auf den Server
- 1. [Rule 1 - Bug] Import-Fix in bestehenden Goldstandard-Tests
- Flask-Login Auth mit /login, /logout, @login_required auf allen Routes, CSRF-Schutz und /health Whitelist
- One-liner:
- Admin-CRUD via /admin/users mit flask create-admin CLI, admin_required Decorator und 6 Integrations-Tests
- Tailwind CSS v3 Build-Pipeline eingerichtet, Bootstrap durch gruenes Sidebar-Dashboard-Layout ersetzt, FMT-10 Doppelpunkt-Splitting mit Untertitel-Beibehaltung implementiert
- One-liner:
- Alle 4 verbleibenden Bootstrap-Templates (churchdesk_events, login, admin/users, admin/edit_user) auf Tailwind CSS umgestellt — Bootstrap komplett eliminiert, alle Icons durch inline SVG ersetzt
- One-liner:
- Flask Settings Blueprint mit Tab-Layout, SMTP-Formular mit Fernet-Verschluesselung, AJAX Test-Mail und Org-Uebersicht
- One-liner:

---
