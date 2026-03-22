# Phase 5: UI Makeover + Formatierung - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Modernes grünes Interface auf Tailwind-Basis, Excel-Import entfernen, Vorschau mit Warnungen, Sonderformat-Titel-Parsing verbessern. Die App bekommt ein visuelles Upgrade ohne funktionale Änderungen an der Kernlogik.

</domain>

<decisions>
## Implementation Decisions

### UI Layout & Design
- Sidebar-Navigation links, Content rechts — klassisches Dashboard-Layout
- Org-Auswahl als Checkboxen in einer Card auf der Hauptseite — wie bisher, aufgehübscht mit Tailwind
- Split-View Vorschau: Links Optionen/Konfiguration, rechts Live-Vorschau des formatierten Textes
- Warnungen als gelbe Alert-Boxen oberhalb des Textes mit Icon
- Grün als Primärfarbe (gesetzt vom User)
- Responsive: kein horizontales Scrollen auf 768px Viewport

### Sonderformat-Titel
- Strikt an Boyens-Referenz halten — keine eigenen Interpretationen
- Boyens-Referenz zeigt: Sonderformate mit Anführungszeichen werden 1:1 übernommen
  - Beispiel: „Unterwegs" Brotzeit: Die Wohnzimmerkirche in Heide (Süd) → exakt so im Output
- Gottesdienst-Titel mit Doppelpunkt: Vor dem Doppelpunkt den Typ matchen (Abendmahl → "Gd. m. A."), nach dem Doppelpunkt den Untertitel anhängen
  - Beispiel: "Gottesdienst mit Abendmahl: Erntedank" → "Gd. m. A. Erntedank"
- Titel die mit Anführungszeichen beginnen (z.B. „Kreuz & Rüben...") → komplett übernehmen, KEIN Typ-Matching
- "Gottesdienst:" allein (nur "Gottesdienst" vor Doppelpunkt) → "Gd." ohne den Rest

### Excel-Entfernung
- Kompletten Excel-Upload-Pfad entfernen: Route, Funktion, Template-Bereich
- pandas und openpyxl aus requirements.txt entfernen (nicht mehr gebraucht)
- Nur noch ChurchDesk-API als Datenquelle

### Tailwind CSS
- Tailwind CSS CLI (Build-Schritt, NICHT CDN — CDN ist laut Tailwind-Docs nicht für Production)
- Tailwind Build-Artefakt in static/css/ ablegen
- Build-Schritt in GitHub Actions CI/CD integrieren
- Kein Node.js im Docker-Container — CSS wird vorab gebaut

### Claude's Discretion
- Exakte Tailwind-Konfiguration (tailwind.config.js)
- Genaue Grün-Töne (Tailwind green-600/700 Palette)
- Sidebar-Breite und Breakpoints
- Icon-Library (Heroicons oder inline SVG)
- Template-Struktur und Partial-Organisation

</decisions>

<canonical_refs>
## Canonical References

### Bestehender Code
- `web/main/routes.py` — Aktuelle Routes, Excel-Upload muss raus
- `web/templates/` — Alle Templates müssen auf Tailwind umgestellt werden
- `web/formatting.py` — format_service_type() für Sonderformat-Parsing
- `web/app.py` — create_app() Factory (Phase 4)

### Boyens-Referenz
- Die offizielle Boyens-Vorgabe ist in .planning/phases/02-formatierung/02-CONTEXT.md dokumentiert (Decisions D-01 bis D-33)
- Sonderformat-Beispiele aus dem April 2026 Export-Test sind im Chat-Verlauf

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- web/templates/base.html — aktuelles Base-Template, wird komplett ersetzt
- web/templates/auth/login.html — Login-Template aus Phase 4, muss auf Tailwind
- web/static/ — Verzeichnis für CSS/Assets existiert

### Established Patterns
- Jinja2 Template-Vererbung mit {% extends "base.html" %}
- Flash-Messages für Feedback
- Blueprint-Organisation (main, auth, admin aus Phase 4)

### Integration Points
- Alle Templates müssen von bestehendem CSS auf Tailwind umgestellt werden
- GitHub Actions Workflow muss Tailwind Build-Schritt bekommen
- Dockerfile muss ggf. static/css/ korrekt kopieren

</code_context>

<specifics>
## Specific Ideas

- Sidebar sollte auf Mobile als Hamburger-Menü kollabieren
- Vorschau-Text in monospace-Font (wie Boyens-Output)
- Copy-to-Clipboard Button prominent neben der Vorschau
- Download-Button (.txt) unter der Vorschau

</specifics>

<deferred>
## Deferred Ideas

- Settings-Seite → Phase 6
- Auto-Mail → Phase 6
- Dark Mode — nicht geplant, aber Tailwind macht es einfach falls gewünscht

</deferred>

---

*Phase: 05-ui-makeover-formatierung*
*Context gathered: 2026-03-22*
