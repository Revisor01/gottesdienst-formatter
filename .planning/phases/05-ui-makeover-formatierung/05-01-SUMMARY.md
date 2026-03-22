---
phase: 05-ui-makeover-formatierung
plan: 01
subsystem: ui
tags: [tailwindcss, flask, jinja2, formatting, sidebar]

# Dependency graph
requires:
  - phase: 04-fundament-auth
    provides: Flask blueprints with login_required, admin routes, base.html with current_user
provides:
  - Tailwind CSS v3 build pipeline (package.json + tailwind.config.js + input.css -> output.css)
  - Green sidebar dashboard layout in base.html (replaces Bootstrap)
  - FMT-10 Doppelpunkt-Split in format_service_type with _match_service_type helper
  - CI/CD Tailwind build step before Docker build
affects: [05-02, 05-03, all templates building on base.html]

# Tech tracking
tech-stack:
  added: [tailwindcss v3.4, @tailwindcss/cli, npm/node build step]
  patterns: [CSS compiled at CI/CD time, no Node.js in Docker container, custom primary green palette]

key-files:
  created:
    - package.json
    - web/tailwind.config.js
    - web/static/css/input.css
    - web/static/css/output.css
  modified:
    - web/templates/base.html
    - web/formatting.py
    - web/tests/test_formatting.py
    - .github/workflows/ci-cd.yml

key-decisions:
  - "Tailwind v3 statt v4 — v4 hat kein tailwind.config.js mehr, v3 einfacher und stabil"
  - "output.css wird committed (nicht .gitignored) — einfacher fuer lokale Entwicklung, CI baut trotzdem frisch"
  - "npm run tw:build mit explizitem -c web/tailwind.config.js Flag — config liegt in web/, package.json im Root"
  - "_match_service_type() extrahiert aus format_service_type() — FMT-10 Doppelpunkt-Split sauber getrennt"
  - "Altes test_format_service_type_sonderformat aktualisiert: Kolon-Untertitel wird jetzt beibehalten (FMT-10 korrekt)"

patterns-established:
  - "Sidebar-Layout: md:ml-56 fuer Content, w-56 Sidebar, -translate-x-full / md:translate-x-0 fuer Mobile-Toggle"
  - "Flash-Messages mit Tailwind alert-* component-Klassen, kein Bootstrap alert"
  - "format_service_type delegiert an _match_service_type; Anfuehrungszeichen-Check vor Doppelpunkt-Check"

requirements-completed: [UI-01, UI-02, FMT-10]

# Metrics
duration: 15min
completed: 2026-03-22
---

# Phase 5 Plan 1: UI-Makeover Fundament Summary

**Tailwind CSS v3 Build-Pipeline eingerichtet, Bootstrap durch gruenes Sidebar-Dashboard-Layout ersetzt, FMT-10 Doppelpunkt-Splitting mit Untertitel-Beibehaltung implementiert**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-22T10:38:00Z
- **Completed:** 2026-03-22T10:52:38Z
- **Tasks:** 2 (Task 1: Tailwind+Layout, Task 2: FMT-10 TDD)
- **Files modified:** 8

## Accomplishments

- Tailwind CSS v3 installiert, package.json mit tw:build Script, Config mit gruener primary-Palette
- base.html komplett von Bootstrap auf Tailwind umgestellt: Sidebar links (w-56, bg-primary-700), Hamburger-Menu auf Mobile, kein Bootstrap mehr
- FMT-10 implementiert: "Gottesdienst mit Abendmahl: Erntedank" -> "Gd. m. A. Erntedank"
- CI/CD Tailwind Build-Step vor Docker-Build in build-and-push Job
- Alle 96 Tests bestehen

## Task Commits

Jede Task wurde atomar committed:

1. **Task 1: Tailwind CSS Setup + Sidebar Layout** - `9227444` (feat)
2. **Task 2 RED: Failing FMT-10 Tests** - `05dd53f` (test)
3. **Task 2 GREEN: FMT-10 Implementation** - `b66dd08` (feat)

## Files Created/Modified

- `package.json` - npm mit tailwindcss devDependency und tw:build/tw:watch Scripts
- `web/tailwind.config.js` - Tailwind-Config mit gruenem primary-Farbschema
- `web/static/css/input.css` - Tailwind-Direktiven + Component-Layer (btn-*, card, input-field, alert-*)
- `web/static/css/output.css` - Kompiliertes CSS-Artefakt (11KB minified)
- `web/templates/base.html` - Sidebar-Dashboard-Layout, Bootstrap vollstaendig entfernt
- `.github/workflows/ci-cd.yml` - setup-node + npm ci + npm run tw:build vor Docker-Build
- `web/formatting.py` - _match_service_type() extrahiert, FMT-10 Doppelpunkt-Split hinzugefuegt
- `web/tests/test_formatting.py` - FMT-10 Tests (test_fmt10_doppelpunkt_split, test_fmt10_anfuehrungszeichen_unveraendert), altes Sonderformat-Test aktualisiert

## Decisions Made

- **Tailwind v3 statt v4**: v4 verwendet keine tailwind.config.js mehr und hat anderen CLI-Befehl — v3 ist stabiler und dokumentierter. Package als `tailwindcss: ^3.4.0`, CLI via `npx tailwindcss`.
- **output.css committed**: Einfacher fuer lokale Entwicklung. CI baut trotzdem frisch vor Docker. Kein .gitignore-Eintrag.
- **Altes Sonderformat-Test geaendert**: Der bestehende Test `"Gottesdienst mit Tisch-Abendmahl: Brot des Lebens" -> "Gd. m. A."` widerspricht FMT-10. Korrekte Erwartung nach FMT-10 ist `"Gd. m. A. Brot des Lebens"` (Untertitel wird beibehalten).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Tailwind v4 nicht kompatibel — auf v3 zurueckgefallen**
- **Found during:** Task 1 (Tailwind CLI Setup)
- **Issue:** Plan erwaehnete `@tailwindcss/cli` (v4-Paket), aber v4 unterstuetzt kein tailwind.config.js und hat anderen CLI-Syntax
- **Fix:** package.json mit `tailwindcss: ^3.4.0` (v3), CLI-Befehl `npx tailwindcss -c web/tailwind.config.js -i ... -o ...`
- **Files modified:** package.json
- **Verification:** npm run tw:build erzeugt output.css ohne Fehler, primary-Farben enthalten
- **Committed in:** 9227444 (Task 1 commit)

**2. [Rule 1 - Bug] Bestehender Sonderformat-Test widersprach FMT-10**
- **Found during:** Task 2 GREEN (nach Implementation)
- **Issue:** `test_format_service_type_sonderformat` erwartete `"Gd. m. A."` fuer `"Gottesdienst mit Tisch-Abendmahl: Brot des Lebens"`, aber FMT-10 erfordert Untertitel-Beibehaltung
- **Fix:** Test auf `"Gd. m. A. Brot des Lebens"` aktualisiert — das ist das korrekte Verhalten nach FMT-10
- **Files modified:** web/tests/test_formatting.py
- **Verification:** Alle 70 Formatting-Tests, alle 96 Tests bestehen
- **Committed in:** b66dd08 (Task 2 GREEN commit)

---

**Total deviations:** 2 auto-fixed (beide Rule 1 - Bug)
**Impact on plan:** Beide Auto-Fixes korrekt. Kein Scope-Creep. Tailwind v3 ist vollwertige Alternative zu v4 fuer diesen Anwendungsfall.

## Issues Encountered

Keine weiteren Probleme ausser den oben dokumentierten Auto-Fixes.

## Known Stubs

Keine — alle implementierten Features sind vollstaendig verdrahtet.

## Next Phase Readiness

- Tailwind Build-Pipeline bereit fuer Plan 02/03 Template-Redesigns
- base.html als Grundlage fuer alle anderen Templates (index.html, login.html etc. muessen ebenfalls auf Tailwind umgestellt werden)
- FMT-10 produktionsbereit, alle Tests grueen
- CI/CD baut Tailwind vor Docker — kein manuelles output.css-Commit noetig nach einmaliger Einrichtung

---
*Phase: 05-ui-makeover-formatierung*
*Completed: 2026-03-22*
