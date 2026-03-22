---
phase: quick
plan: 260322-kaw
type: execute
wave: 1
depends_on: []
files_modified:
  - web/config.py
  - web/admin/routes.py
  - web/admin/forms.py
  - web/templates/admin/organizations.html
  - web/templates/admin/edit_org.html
  - web/templates/settings/settings.html
  - web/templates/base.html
  - web/docker-compose.prod.yml
autonomous: true
requirements: []

must_haves:
  truths:
    - "Organisationen werden aus data/organizations.json geladen statt ENV-Vars"
    - "Admin kann Organisationen hinzufuegen, bearbeiten und loeschen ueber /admin/organizations"
    - "Org 2719 ist nicht mehr enthalten"
    - "Beim ersten Start werden ENV-Vars automatisch nach JSON migriert"
    - "Settings Org-Tab verlinkt auf die Admin-Verwaltung"
  artifacts:
    - path: "web/config.py"
      provides: "JSON-first load_organizations() mit ENV-Fallback und Migration"
    - path: "web/admin/routes.py"
      provides: "CRUD-Routes fuer /admin/organizations"
    - path: "web/templates/admin/organizations.html"
      provides: "Org-Tabelle mit Add/Edit/Delete"
    - path: "web/templates/admin/edit_org.html"
      provides: "Formular fuer Org erstellen/bearbeiten"
  key_links:
    - from: "web/config.py"
      to: "web/data/organizations.json"
      via: "json.load/json.dump"
    - from: "web/admin/routes.py"
      to: "web/config.py"
      via: "save_organizations() und load_organizations()"
    - from: "web/churchdesk_api.py"
      to: "web/config.py"
      via: "from config import ORGANIZATIONS (unveraendert)"
---

<objective>
Organisationsverwaltung von Environment-Variablen auf JSON-Datei (data/organizations.json) umstellen mit Web-basierter Admin-CRUD-Oberflaeche.

Purpose: Orgs sollen ohne Server-Neustart und ENV-Aenderungen verwaltet werden koennen.
Output: JSON-basierte Org-Konfiguration + Admin-UI unter /admin/organizations + ENV-Migration
</objective>

<context>
@web/config.py
@web/admin/routes.py
@web/admin/forms.py
@web/templates/admin/users.html
@web/templates/admin/edit_user.html
@web/templates/settings/settings.html
@web/docker-compose.prod.yml

<interfaces>
<!-- Bestehende Importe die unveraendert bleiben muessen -->
From web/config.py (importiert von 4 Modulen):
```python
from config import ORGANIZATIONS
# ORGANIZATIONS: dict[int, {"name": str, "token": str, "description": str}]
```

From web/admin/routes.py:
```python
def admin_required(f):  # Existierender Decorator — wiederverwenden
```

From web/admin/forms.py:
```python
# Pattern: FlaskForm mit Validatoren, SubmitField
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: config.py auf JSON umstellen + save/reload Funktionen</name>
  <files>web/config.py</files>
  <action>
config.py komplett umschreiben:

1. `_json_path()` — Gibt `os.path.join(os.path.dirname(__file__), 'data', 'organizations.json')` zurueck.

2. `load_organizations() -> dict` — Neue Logik:
   - Wenn `data/organizations.json` existiert: JSON laden, Keys zu int casten, zurueckgeben.
   - Wenn JSON nicht existiert aber CHURCHDESK_ORG_IDS ENV-Var gesetzt: alte ENV-Logik ausfuehren, Ergebnis als JSON speichern (Migration), Log-Meldung ausgeben.
   - Wenn weder JSON noch ENV: leeres dict zurueckgeben.
   - WICHTIG: Org 2719 bei Migration NICHT uebernehmen (explizit filtern).

3. `save_organizations(orgs: dict) -> None` — Neues dict nach `data/organizations.json` schreiben. Keys als Strings im JSON (JSON kennt keine int-Keys). `os.makedirs` fuer data/ Verzeichnis. `json.dump` mit `indent=2, ensure_ascii=False`.

4. `reload_organizations() -> dict` — Ruft `load_organizations()` auf und aktualisiert das globale `ORGANIZATIONS` dict in-place (`.clear()` + `.update()`). Gibt das aktualisierte dict zurueck. Wird nach jedem CRUD-Vorgang aufgerufen.

5. `ORGANIZATIONS = load_organizations()` bleibt am Modulende — alle bestehenden `from config import ORGANIZATIONS` Importe funktionieren weiterhin unveraendert.

WICHTIG: Das ORGANIZATIONS-Dict muss in-place aktualisiert werden (nicht neu zugewiesen), weil andere Module es per `from config import ORGANIZATIONS` importiert haben und eine Neuzuweisung die Referenz bricht.
  </action>
  <verify>
    <automated>cd /Users/simonluthe/Documents/kk-termine && python -c "
import sys; sys.path.insert(0, 'web')
from config import load_organizations, save_organizations, reload_organizations, ORGANIZATIONS, _json_path
import os, json

# Test: Wenn JSON existiert, laden
path = _json_path()
os.makedirs(os.path.dirname(path), exist_ok=True)
test_data = {2596: {'name': 'Test', 'token': 'abc', 'description': ''}}
save_organizations(test_data)
loaded = load_organizations()
assert loaded[2596]['name'] == 'Test', 'JSON load failed'
assert isinstance(list(loaded.keys())[0], int), 'Keys must be int'

# Test: reload aktualisiert globales dict
test_data[9999] = {'name': 'New', 'token': 'xyz', 'description': ''}
save_organizations(test_data)
reload_organizations()
assert 9999 in ORGANIZATIONS, 'reload did not update global dict'

# Cleanup
os.remove(path)
print('ALL TESTS PASSED')
"
    </automated>
  </verify>
  <done>config.py laedt aus JSON, faellt auf ENV zurueck, migriert automatisch, save/reload funktionieren, ORGANIZATIONS-Referenz bleibt stabil</done>
</task>

<task type="auto">
  <name>Task 2: Admin CRUD-Routes + Templates + Forms fuer Organisationen</name>
  <files>web/admin/routes.py, web/admin/forms.py, web/templates/admin/organizations.html, web/templates/admin/edit_org.html, web/templates/settings/settings.html, web/templates/base.html, web/docker-compose.prod.yml</files>
  <action>
**web/admin/forms.py** — Zwei neue Forms hinzufuegen (UNTER den bestehenden):

```python
class OrganizationForm(FlaskForm):
    org_id = StringField('Organisations-ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(max=200)])
    token = StringField('API-Token', validators=[DataRequired()])
    description = StringField('Beschreibung')
    submit = SubmitField('Speichern')
```

**web/admin/routes.py** — 4 neue Routes hinzufuegen (UNTER bestehenden):

Import ergaenzen: `from config import ORGANIZATIONS, save_organizations, reload_organizations` und `from admin.forms import CreateUserForm, EditUserForm, OrganizationForm`.

1. `GET /admin/organizations` — Liste aller Orgs als Tabelle. Template: `admin/organizations.html`. Uebergibt `organizations=ORGANIZATIONS`.

2. `GET+POST /admin/organizations/new` — Neue Org anlegen. Bei POST: org_id aus Formular parsen (muss int sein), pruefen ob ID schon existiert (flash error), ORGANIZATIONS[org_id] setzen, save_organizations(ORGANIZATIONS), reload_organizations(), flash success, redirect zur Liste.

3. `GET+POST /admin/organizations/<int:org_id>/edit` — Org bearbeiten. Bei GET: Formular vorausfuellen (org_id readonly). Bei POST: Name/Token/Description updaten, save + reload, redirect.

4. `POST /admin/organizations/<int:org_id>/delete` — Org loeschen. Aus ORGANIZATIONS entfernen, save + reload, flash, redirect. Kein GET (nur POST mit CSRF).

Alle Routes mit `@admin_required`.

**web/templates/admin/organizations.html** — Analog zu users.html:
- Titel "Organisationen" mit "Neue Organisation" Button (rechts, btn-primary, Link auf admin.create_org)
- Card > overflow-x-auto > table.w-full (gleiches Pattern wie users.html)
- Spalten: ID, Name, Beschreibung, Token (gekuerzt: erste 8 Zeichen + "..."), Aktionen
- Aktionen: "Bearbeiten" Link + "Loeschen" Button (kleines form mit POST + csrf_token + onclick="return confirm('Organisation wirklich loeschen?')")
- Leerer Zustand: "Keine Organisationen konfiguriert."

**web/templates/admin/edit_org.html** — Analog zu edit_user.html:
- Titel: "Neue Organisation" bzw. "Organisation bearbeiten"
- Formularfelder: org_id (bei Edit readonly/disabled + hidden field fuer POST), name, token (type=text, vollstaendig sichtbar), description
- Buttons: Speichern + Abbrechen (Link auf admin.organizations)

**web/templates/settings/settings.html** — Org-Tab updaten (Zeilen 187-208 ersetzen):
- Statt readonly Karten: Kurze Info "X Organisationen konfiguriert" + Button/Link "Organisationen verwalten" der auf url_for('admin.organizations') zeigt.
- Fuer Nicht-Admins: Weiterhin die readonly Karten-Ansicht (bestehender Code).
- Pruefen mit `current_user.is_admin`.

**web/templates/base.html** — Neuen Nav-Link "Organisationen" im Admin-Bereich der Sidebar hinzufuegen (nach dem Benutzer-Link, gleiche Struktur, Icon: Heroicon "building-office" oder aehnliches SVG). Link auf `url_for('admin.organizations')`. Nur sichtbar wenn `current_user.is_admin`.

**web/docker-compose.prod.yml** — Alle CHURCHDESK_ORG_* Zeilen entfernen (Zeilen 16-31). Nur SECRET_KEY und FLASK_* behalten. Kommentar hinzufuegen: `# Organisationen werden ueber /admin/organizations verwaltet (data/organizations.json)`.
  </action>
  <verify>
    <automated>cd /Users/simonluthe/Documents/kk-termine && python -c "
import sys; sys.path.insert(0, 'web')
# Verify forms importable
from admin.forms import OrganizationForm
f = OrganizationForm
assert hasattr(f, 'org_id'), 'Missing org_id field'
assert hasattr(f, 'name'), 'Missing name field'
assert hasattr(f, 'token'), 'Missing token field'
print('Forms OK')
" && grep -q 'organizations' web/admin/routes.py && echo "Routes OK" && test -f web/templates/admin/organizations.html && echo "Template OK" && ! grep -q 'CHURCHDESK_ORG' web/docker-compose.prod.yml && echo "Docker cleanup OK" && echo "ALL CHECKS PASSED"
    </automated>
  </verify>
  <done>Admin kann unter /admin/organizations Orgs sehen, hinzufuegen, bearbeiten und loeschen. Settings Org-Tab verlinkt auf Admin-Verwaltung. docker-compose.prod.yml hat keine CHURCHDESK_ORG_* ENV-Vars mehr.</done>
</task>

</tasks>

<verification>
1. `cd web && python -c "from config import ORGANIZATIONS; print(len(ORGANIZATIONS), 'orgs loaded')"` — Orgs werden geladen
2. `grep -c 'CHURCHDESK_ORG' web/docker-compose.prod.yml` — Muss 0 sein
3. `grep 'admin.organizations' web/templates/base.html` — Nav-Link existiert
4. Manuell: App starten, /admin/organizations aufrufen, Org hinzufuegen/bearbeiten/loeschen testen
</verification>

<success_criteria>
- Organisationen werden aus data/organizations.json geladen (nicht ENV)
- Admin-UI unter /admin/organizations funktioniert (CRUD)
- Org 2719 ist nicht mehr enthalten
- ENV-Fallback mit automatischer Migration funktioniert
- docker-compose.prod.yml hat keine CHURCHDESK_ORG_* Variablen mehr
- Bestehende Importe (`from config import ORGANIZATIONS`) funktionieren unveraendert
</success_criteria>

<output>
Nach Abschluss: `.planning/quick/260322-kaw-org-verwaltung-im-web-interface-statt-en/260322-kaw-SUMMARY.md` erstellen
</output>
