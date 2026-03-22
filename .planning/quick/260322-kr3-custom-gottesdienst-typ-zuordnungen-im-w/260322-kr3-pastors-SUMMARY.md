# Pastor-Formatierung: DB-Lookup statt Regex

**One-liner:** Pastor-Formatierung komplett auf DB-Lookup umgebaut — neues Pastor-Modell mit first_name/last_name/title, 24 Seed-Eintraege aus April-Export, Admin-CRUD unter /admin/pastors, format_pastor() ist jetzt rein Nachname-basiert ohne Regex.

## Was wurde gebaut

### Neues DB-Modell `Pastor`
- Tabelle `pastors` mit: id, first_name (nullable), last_name, title, is_active
- Migration: `f8614177200d_add_pastor_model.py`
- Disambiguierung: gleicher Nachname (Verwold, Thom) via optionalem Vorname

### `format_pastor()` — vollstaendiger Umbau
**Vorher:** Regex-basiertes Prefix-Stripping (Pastor, Pastorin, P., Pn., etc.), dann Nachname-Extraktion, dann manuelles Titelmapping.

**Nachher:** Rein DB-Lookup-basiert.
1. Split Contributor-String an ` & `, ` und `, ` + `, ` / ` (Komma als Fallback)
2. Fuer jeden Teil: `_lookup_pastor()` sucht ob ein bekannter `last_name` im Text vorkommt
3. Bei Match: ausgabe als `"Titel Nachname"` (z.B. `"P. Luthe"`)
4. Bei Mehrdeutigkeit (Verwold/Thom): `first_name` zur Disambiguierung, sonst erster Treffer
5. Kein Match: unveraendert durchreichen (Kantorei, Frauenhilfe, Team, etc.)

### Seed-Daten (24 Pastoren)
Alle Mitwirkenden aus April 2026 Export erfasst. Problematische Faelle:
- Verwold: Christian → P., Ulrike → Pn. (via first_name disambiguiert)
- Thom: zwei Eintraege ohne Vorname (erster Treffer gewinnt — hier wuenschenswert Vornamen nachzutragen)
- Stein: title = "P. Dr." (Dr. ist Teil der Abkuerzung)

### Admin-CRUD `/admin/pastors`
- Liste mit Ausgabe-Preview-Spalte ("P. Luthe")
- Erstellen/Bearbeiten/Loeschen mit Cache-Reload
- Sidebar-Link in Admin-Sektion

## Dateien

### Erstellt
- `web/migrations/versions/f8614177200d_add_pastor_model.py`
- `web/templates/admin/pastors.html`
- `web/templates/admin/edit_pastor.html`

### Geaendert
- `web/models.py` — Pastor-Klasse hinzugefuegt
- `web/formatting.py` — format_pastor() komplett neu, _pastor_cache, load_pastors(), reload_pastors()
- `web/app.py` — load_pastors() beim Start, seed-pastors CLI-Kommando
- `web/admin/routes.py` — Pastor CRUD-Routen und _reload_pastors()
- `web/admin/forms.py` — PastorForm
- `web/templates/base.html` — Sidebar-Link Pastoren

## Commits

| Hash | Beschreibung |
|------|-------------|
| 754053e | feat: add Pastor DB model |
| 6951ff1 | feat: rewrite format_pastor() with DB-lookup |
| 9921bb1 | feat: add Pastor admin CRUD at /admin/pastors |

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- web/models.py: Pastor-Klasse vorhanden
- web/formatting.py: _pastor_cache, load_pastors, format_pastor mit DB-Lookup
- web/app.py: load_pastors() und seed-pastors Kommando
- web/admin/routes.py: pastors, create_pastor, edit_pastor, delete_pastor Routen
- web/templates/admin/pastors.html: vorhanden
- web/templates/admin/edit_pastor.html: vorhanden
- Smoke-Test: 6/6 format_pastor()-Tests bestanden
