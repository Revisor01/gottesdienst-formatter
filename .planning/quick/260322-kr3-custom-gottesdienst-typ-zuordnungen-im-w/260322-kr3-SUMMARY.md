---
phase: quick
plan: 260322-kr3
subsystem: admin/formatting
tags: [admin, service-types, custom-mappings, formatting]
key-files:
  created:
    - web/migrations/versions/f1a2b3c4d5e6_add_service_type_mappings_table.py
    - web/templates/admin/service_types.html
    - web/templates/admin/edit_service_type.html
  modified:
    - web/models.py
    - web/formatting.py
    - web/app.py
    - web/admin/forms.py
    - web/admin/routes.py
    - web/templates/base.html
decisions:
  - keyword wird beim Speichern auf Lowercase normalisiert (strip().lower()) damit Case-Inkonsistenz keine doppelten Eintraege erzeugt
  - reload_custom_mappings ist ein Alias fuer load_custom_mappings — expliziterer Name fuer post-CRUD-Aufrufe
  - _reload_service_types() nutzt current_app._get_current_object() um den echten App-Proxy aufzuloesen
metrics:
  completed: 2026-03-22
  tasks: 8
  files: 8
---

# Quick Task 260322-kr3: Custom Gottesdienst-Typ-Zuordnungen im Web-Interface

**One-liner:** Admin-CRUD fuer custom Keyword-zu-Label-Mappings mit Prioritaet, die vor den eingebauten Typ-Regeln in formatting.py geprueft werden.

## Was wurde gebaut

- **ServiceTypeMapping-Model** in models.py: keyword (unique), output_label, priority, is_active
- **Alembic-Migration** f1a2b3c4d5e6 mit Seed-Eintrag: wohnzimmerkirche -> Wz-Gd. (priority 100)
- **formatting.py**: `_custom_mappings`-Cache, `load_custom_mappings(app)`, `reload_custom_mappings(app)`; `_match_service_type()` prueft Custom-Mappings zuerst (sortiert nach priority DESC)
- **app.py**: `load_custom_mappings(app)` wird beim App-Start nach `reload_organizations()` aufgerufen
- **admin/forms.py**: `ServiceTypeMappingForm` (keyword, output_label, priority, is_active)
- **admin/routes.py**: CRUD unter `/admin/service-types` (list, new, edit, delete), nach jeder Schreiboperation `_reload_service_types()`
- **Templates**: service_types.html (Tabelle) und edit_service_type.html (Formular), Stil analog zu organizations.html
- **base.html**: Sidebar-Link "Typ-Zuordnungen" fuer Admins unter Organisationen

## Commits

- d0ee0c3: feat: add ServiceTypeMapping model and Alembic migration
- 52ed55d: feat: add custom mapping cache to formatting.py, load on app startup
- 39272a7: feat: add CRUD routes and form for ServiceTypeMapping in admin
- 97ea8b2: feat: add admin templates for service type mappings and sidebar link

## Deviations from Plan

None — Plan exakt wie beschrieben umgesetzt.

## Known Stubs

None.

## Self-Check: PASSED

- web/models.py ServiceTypeMapping: FOUND
- web/migrations/versions/f1a2b3c4d5e6_add_service_type_mappings_table.py: FOUND
- web/formatting.py _custom_mappings + load_custom_mappings: FOUND
- web/app.py load_custom_mappings call: FOUND
- web/admin/forms.py ServiceTypeMappingForm: FOUND
- web/admin/routes.py service_types routes: FOUND
- web/templates/admin/service_types.html: FOUND
- web/templates/admin/edit_service_type.html: FOUND
- web/templates/base.html Typ-Zuordnungen link: FOUND
