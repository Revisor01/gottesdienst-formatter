# Phase 1: Stabilisierung - Research

**Researched:** 2026-03-21
**Domain:** Python/Flask brownfield refactoring — security hardening, code consolidation
**Confidence:** HIGH (all findings verified directly in source code)

## Summary

Phase 1 bereinigt eine funktionierende aber technisch verschuldete Flask-Anwendung in drei Bereichen: Sicherheit (hardcoded Credentials), Codeduplizierung (dreifache Formatierungslogik) und Erweiterbarkeit (neue Orgas erfordern aktuell Code-Änderungen).

Der konkrete Zustand ist durch direkte Codeanalyse vollständig dokumentiert. SEC-01 und SEC-02 sind triviale Einzeiler — die echte Arbeit liegt in CODE-01 bis CODE-04: das Extrahieren eines `formatting.py`-Moduls und das Umbauen der `ORGANIZATIONS`-Konfiguration auf reine Env-Var-Steuerung ohne hardcoded Fallbacks.

**Primary recommendation:** Neues Modul `web/formatting.py` als einzige Quelle der Wahrheit für alle Formatierungsfunktionen. `ORGANIZATIONS`-Dict vollständig aus dem Quellcode entfernen, durch env-var-basiertes Laden zur Runtime ersetzen.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SEC-01 | Alle API-Tokens aus Quellcode entfernt, nur via Environment Variables geladen | Tokens in `churchdesk_api.py` Z. 15-41 vollständig inventarisiert; Env-Var-Pattern in `create_api_client()` Z. 514-537 existiert bereits als Vorlage |
| SEC-02 | Flask Secret Key via Environment Variable, nicht hardcoded | Einzeilige Änderung in `web/app.py` Z. 19 |
| CODE-01 | Formatierungslogik in einem zentralen Modul (nicht 3x dupliziert) | `format_date`, `format_time`, `format_service_type` identisch in `gottesdienst_formatter_final.py` Z. 18-86 und `web/app.py` Z. 36-101 |
| CODE-02 | Pastor-Formatierung: eine konsolidierte Implementierung | Drei Varianten inventarisiert: `format_pastor()` in app.py Z. 103-125, in formatter_final.py Z. 88-114, und `format_boyens_pastor()` in churchdesk_api.py Z. 358-422 |
| CODE-03 | Klare Schichtentrennung: API-Client / Formatierung / Web-Interface | Aktuell liegt Formatierungslogik in app.py UND churchdesk_api.py — muss in eigenes Modul |
| CODE-04 | Neue ChurchDesk-Organisation hinzufügen erfordert nur Konfiguration, keinen Code-Change | Aktuell: `ORGANIZATIONS`-Dict hardcoded + Checkbox in `index.html` hardcoded — beide müssen konfigurierbar werden |
</phase_requirements>

## Exact Code Inventory

### SEC-01: Hardcoded API Tokens

**Datei:** `web/churchdesk_api.py` Z. 15-41

```python
ORGANIZATIONS = {
    2596: {'name': 'Kirchenkreis Dithmarschen', 'token': 'd4ec66780546786c92b916f873ee713181c1b695d32e7ba9839e760eaecd3fa1', ...},
    6572: {'name': 'Kirchspiel Heide',           'token': '7b0cf910b378c6d2482419f4e785fc95b18c1ec6fbfdd6dea48085b58f52e894', ...},
    2719: {'name': 'KG Hennstedt (alt)',          'token': 'c2d76c9414f6aac773c1643a98131123dbfc2ae7c31e4d2e864974c131dccedf', ...},
    2725: {'name': 'Kirchspiel Eider',            'token': '3afe57b4ae54ece02ff568993777028b47995601ecab92097e30a66f4d90494d', ...},
    2729: {'name': 'Kirchspiel West',             'token': 'bZq4GLCvhUbkYFQrDVDAe3cTs8hVlyQqEUmQ6xW5Tjw2EMEm3lCgYI6LSj3lrhvf7MTDIHL3TdrVXYdV', ...},
}
```

Zusätzlicher Fallback in `docker-compose.yml` Z. 15:
```yaml
- CHURCHDESK_API_TOKEN=${CHURCHDESK_API_TOKEN:-d4ec66780546786c92b916f873ee713181c1b695d32e7ba9839e760eaecd3fa1}
```

**Alle 5 Tokens sind im Git-History kompromittiert und müssen nach der Umstellung rotiert werden.**

### SEC-02: Hardcoded Flask Secret Key

**Datei:** `web/app.py` Z. 19

```python
app.secret_key = 'gottesdienst-formatter-secret-key'
```

### CODE-01 / CODE-03: Dreifach duplizierte Formatierungsfunktionen

| Funktion | gottesdienst_formatter_final.py | web/app.py | web/churchdesk_api.py |
|----------|--------------------------------|------------|----------------------|
| `format_date()` | Z. 18-39 | Z. 36-56 | — (fehlt, app.py-Version wird via Import genutzt) |
| `format_time()` | Z. 41-52 | Z. 58-69 | — |
| `format_service_type()` | Z. 54-86 (ohne Tauffest/Goldene Konfirmation) | Z. 71-101 (mit Tauffest/Goldene Konfirmation) | — |
| `format_pastor()` | Z. 88-114 | Z. 103-125 | als `format_boyens_pastor()` Z. 358-422 |

**Unterschiede zwischen den Versionen:**
- `format_service_type()` in `app.py` hat Tauffest, Diamantene/Goldene/Silberne Konfirmation, Abendsegen — der standalone-Script hat diese nicht
- `format_pastor()` in `app.py` und `formatter_final.py` sind identisch und haben deutlich weniger Logik als `format_boyens_pastor()` in `churchdesk_api.py`
- `format_boyens_pastor()` unterstützt: mehrere Mitwirkende (via Delimiter-Split), Diakonin (Dn.), Diakon (D.), Pastores (Ps.), Prädikant — die anderen Varianten nicht
- `format_boyens_pastor()` ist die vollständigere Implementierung und sollte die Grundlage sein

### CODE-02: Pastor-Formatierungsunterschiede im Detail

**`format_pastor()` in app.py / formatter_final.py (vereinfacht):**
- Kein Delimiter-Splitting (nur ein Mitwirkender)
- Unbekannte Präfixe → immer "P." (Fallback)
- Kein Diakonin (Dn.), kein Pastores (Ps.)

**`format_boyens_pastor()` in churchdesk_api.py (vollständig):**
- Delimiter-Splitting: `, ` / ` & ` / ` und ` / ` + ` / ` / `
- Sonderfall "Kirchspiel-Pastor:innen", "Konfirmand:innen"
- Vollständige Prefix-Liste inkl. Diakonin, Diakon, Pastores
- Unbekannte Präfixe → Original beibehalten (kein erzwungenes "P.")
- Rückgabe mit ` & ` verbunden

**Konsolidierungsstrategie:** `format_boyens_pastor()` ist die kanonische Implementierung. Die Excel-Pfad-Funktion `format_pastor()` wird auf Wrapper-Aufruf von `format_boyens_pastor()` reduziert oder direkt ersetzt.

### CODE-04: Neue Organisation hinzufügen erfordert aktuell zwei Code-Änderungen

**Schritt 1 — Code in `churchdesk_api.py` Z. 15-41:** `ORGANIZATIONS`-Dict erweitern
**Schritt 2 — Template in `web/templates/index.html`:** Hardcoded Checkbox-Liste erweitern

Das Ziel ist: Neue Org nur durch Env-Var-Eintrag (z.B. `CHURCHDESK_ORG_1234_NAME`, `CHURCHDESK_ORG_1234_TOKEN`) einbinden — kein Code-Change, kein Template-Edit.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | aktuell (web/requirements.txt) | Web-Framework | Bereits im Einsatz |
| python-dotenv | 1.0.x | `.env`-Datei laden für Development | Industriestandard für lokale Env-Vars |
| os.environ | stdlib | Env-Vars in Produktion lesen | Kein Extra-Paket nötig |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.0.x | Lokales Development mit `.env` | Verhindert Export von Tokens in Shell |

**Installation:**
```bash
pip install python-dotenv
```

**Hinweis:** `python-dotenv` wird nur für lokales Development benötigt. Im Docker-Container kommen Env-Vars direkt aus `docker-compose.yml` → keine Änderung am Produktions-Setup nötig.

## Architecture Patterns

### Target Project Structure
```
web/
├── app.py                  # Flask routes only — keine Formatierungslogik mehr
├── formatting.py           # NEUES Modul: alle format_* Funktionen
├── churchdesk_api.py       # API-Client only — format_boyens_pastor bleibt hier oder zieht zu formatting.py
├── config.py               # NEUES Modul: Org-Konfiguration aus Env-Vars laden
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── templates/
    ├── base.html
    ├── index.html           # Org-Liste dynamisch aus Config generieren
    ├── result.html
    └── churchdesk_events.html
gottesdienst_formatter_final.py  # Importiert aus web/formatting.py statt eigener Kopie
```

### Pattern 1: Formatting Module Extraction
**What:** Alle `format_*`-Funktionen in `web/formatting.py` verschieben
**When to use:** Sofort — das ist das Kernstück dieser Phase
**Example:**
```python
# web/formatting.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def format_date(date_obj):
    """..."""
    ...

def format_time(date_obj):
    """..."""
    ...

def format_service_type(titel):
    """..."""
    ...

def format_pastor(contributor: str) -> str:
    """Kanonische Pastor-Formatierung (war: format_boyens_pastor)"""
    ...
```

```python
# web/app.py — nach Refactoring
from formatting import format_date, format_time, format_service_type, format_pastor
```

```python
# web/churchdesk_api.py — nach Refactoring
from formatting import format_pastor  # format_boyens_pastor entfernt
```

```python
# gottesdienst_formatter_final.py — nach Refactoring
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web'))
from formatting import format_date, format_time, format_service_type, format_pastor
```

### Pattern 2: Config-driven Organization Loading (CODE-04)
**What:** ORGANIZATIONS-Dict nicht mehr hardcoded, sondern zur Runtime aus Env-Vars aufgebaut
**When to use:** `web/config.py` neu erstellen

```python
# web/config.py
import os

def load_organizations() -> dict:
    """Lädt Organisationskonfiguration aus Env-Vars.

    Erwartet Env-Vars in Format:
        CHURCHDESK_ORG_{ID}_NAME=Kirchspiel Heide
        CHURCHDESK_ORG_{ID}_TOKEN=abc123...
        CHURCHDESK_ORG_{ID}_DESCRIPTION=Heide (St.-Jürgen...)  # optional

    Beispiel für 3 Orgs: IDs via CHURCHDESK_ORG_IDS=2596,6572,2725
    """
    org_ids_str = os.getenv('CHURCHDESK_ORG_IDS', '')
    if not org_ids_str:
        return {}

    orgs = {}
    for org_id_str in org_ids_str.split(','):
        org_id = int(org_id_str.strip())
        prefix = "CHURCHDESK_ORG_{}_".format(org_id)
        name = os.getenv("{}NAME".format(prefix))
        token = os.getenv("{}TOKEN".format(prefix))
        if name and token:
            orgs[org_id] = {
                'name': name,
                'token': token,
                'description': os.getenv("{}DESCRIPTION".format(prefix), '')
            }
    return orgs

ORGANIZATIONS = load_organizations()
```

**docker-compose.yml-Erweiterung:**
```yaml
environment:
  - FLASK_ENV=production
  - SECRET_KEY=${SECRET_KEY}
  - CHURCHDESK_ORG_IDS=2596,6572,2719,2725,2729
  - CHURCHDESK_ORG_2596_NAME=Kirchenkreis Dithmarschen
  - CHURCHDESK_ORG_2596_TOKEN=${CHURCHDESK_ORG_2596_TOKEN}
  - CHURCHDESK_ORG_6572_NAME=Kirchspiel Heide
  - CHURCHDESK_ORG_6572_TOKEN=${CHURCHDESK_ORG_6572_TOKEN}
  # ... weitere Orgs
```

**index.html — dynamische Org-Liste:**
```html
{% for org_id, org in organizations.items() %}
<div class="form-check">
  <input class="form-check-input" type="checkbox" name="selected_organizations"
         value="{{ org_id }}" id="org{{ org_id }}">
  <label class="form-check-label" for="org{{ org_id }}">
    {{ org.name }}
    {% if org.description %}<small class="text-muted">— {{ org.description }}</small>{% endif %}
  </label>
</div>
{% endfor %}
```

### Pattern 3: SEC-01/SEC-02 Secret Key Fix
```python
# web/app.py
import os
import secrets

app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)
```

Der `secrets.token_hex(32)`-Fallback ist sicher für Development (neuer Key pro Restart), aber macht Sessions ungültig. Für Produktion MUSS `SECRET_KEY` als Env-Var gesetzt sein.

### Anti-Patterns to Avoid
- **Hardcoded Fallbacks im Code:** `os.getenv('TOKEN', 'hardcoded_token')` ist genauso schlecht wie direkt hardcoded — kein Fallback auf alte Tokens
- **Teilweise Migration:** Alte `ORGANIZATIONS`-Dict behalten UND neue Config-Funktion parallel — führt zu Verwirrung welche Quelle gilt
- **format_boyens_pastor umbenennen aber Signatur brechen:** `app.py` importiert aktuell `format_boyens_pastor` direkt — Rename muss Imports mitziehen

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Env-Var-Laden mit .env-Support | Eigenes Parsing | `python-dotenv` | Behandelt Quotes, Multiline, Encoding korrekt |
| Sicherer Secret Key | Eigene UUID-Generierung | `secrets.token_hex(32)` | stdlib, kryptographisch sicher |
| Env-Var-Prefix-Pattern | Komplexes String-Parsing | `os.getenv()` mit definiertem Prefix-Schema | Einfach und ausreichend |

## Common Pitfalls

### Pitfall 1: format_pastor vs. format_boyens_pastor — welche ist kanonisch?
**What goes wrong:** Man behält beide, benennt keine um, Code importiert unterschiedliche Versionen
**Why it happens:** Rename ist "riskant", man will nichts brechen
**How to avoid:** `format_boyens_pastor` → `format_pastor` umbenennen. Alle drei Aufrufstellen aktualisieren. Die schwächere Variante in `app.py` löschen.
**Warning signs:** Beide Funktionen existieren noch nach Phase 1

### Pitfall 2: docker-compose.yml hat noch hardcoded Token-Fallbacks
**What goes wrong:** `${TOKEN:-hardcoded_value}` in docker-compose.yml bleibt stehen, Sicherheitslücke bleibt
**Why it happens:** Nur der Python-Code wird bereinigt, compose-Datei wird vergessen
**How to avoid:** docker-compose.yml explizit prüfen und Fallback-Werte entfernen
**Warning signs:** `:-` in Env-Var-Definitionen in docker-compose.yml

### Pitfall 3: Standalone-Script verliert Import-Pfad
**What goes wrong:** `gottesdienst_formatter_final.py` im Root kann `from web.formatting import ...` nicht auflösen
**Why it happens:** Python-Pfad unterscheidet sich je nach Ausführungskontext
**How to avoid:** `sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web'))` am Script-Anfang
**Warning signs:** `ModuleNotFoundError` beim direkten Aufruf des Standalone-Scripts

### Pitfall 4: index.html zeigt leere Org-Liste wenn Env-Vars fehlen
**What goes wrong:** Wenn `CHURCHDESK_ORG_IDS` nicht gesetzt, ist `ORGANIZATIONS` leer — UI zeigt keine Checkboxen
**Why it happens:** Kein Fallback-Hinweis für den Nutzer
**How to avoid:** Template-Check: `{% if not organizations %}` → Fehlermeldung "Keine Organisationen konfiguriert"
**Warning signs:** Leere Checkbox-Liste ohne Fehlermeldung

### Pitfall 5: pd.isna()-Abhängigkeit in format_date / format_time
**What goes wrong:** `format_date()` in `app.py` ruft `pd.isna()` auf — wenn das Modul nach `formatting.py` verschoben wird, muss `import pandas as pd` mitgehen oder durch `isinstance(date_obj, float) and math.isnan(date_obj)` ersetzt werden
**Why it happens:** Das neue Modul ist von pandas abhängig, was für ChurchDesk-Pfad unnötig ist
**How to avoid:** In `formatting.py` pandas importieren (ist sowieso Abhängigkeit), oder Guard gegen None statt pd.isna()
**Warning signs:** `NameError: name 'pd' is not defined` in formatting.py

## Code Examples

### Aktueller Zustand: format_service_type — Versionsunterschied

```python
# gottesdienst_formatter_final.py Z. 54-86 — UNVOLLSTÄNDIG
def format_service_type(titel):
    if 'abendmahl' in titel_lower:
        return 'Gd. m. A.'
    elif 'taufe' in titel_lower:
        return 'Gd. m. T.'
    elif 'konfirmation' in titel_lower:      # <-- Kein Tauffest, keine Gold/Silber-Konfirmation
        return 'Konfirmation'
    ...

# web/app.py Z. 71-101 — VOLLSTÄNDIGER (hat Tauffest, Diamantene/Goldene/Silberne Konfirmation, Abendsegen)
def format_service_type(titel):
    if 'tauffest' in titel_lower:
        return 'Tauffest'
    elif 'diamantene konfirmation' in titel_lower:
        return 'Diamantene Konfirmation'
    ...
```

Die `web/app.py`-Version ist die vollständigere — sie wird die Grundlage für `formatting.py`.

### Ziel-Zustand: web/app.py nach Refactoring (Security)

```python
# web/app.py Z. 19 — VORHER
app.secret_key = 'gottesdienst-formatter-secret-key'

# web/app.py Z. 19 — NACHHER
import secrets
app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)
```

### Ziel-Zustand: churchdesk_api.py — ORGANIZATIONS entfernen

```python
# VORHER: churchdesk_api.py Z. 15-41
ORGANIZATIONS = {
    2596: {'name': '...', 'token': 'hardcoded...'},
    ...
}

# NACHHER: churchdesk_api.py importiert aus config.py
from config import ORGANIZATIONS
```

## Runtime State Inventory

> Diese Phase ist kein Rename/Refactor im Sinne von Datenmigration, aber API-Token-Rotation ist ein Runtime-State-Problem.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | Keine Daten in DB oder Datastore | None |
| Live service config | ChurchDesk API: 5 Tokens in Git-History kompromittiert | Alle 5 Tokens rotieren NACH dem Deployment der env-var-basierten Version |
| OS-registered state | Keine Task Scheduler / Cron-Jobs mit Token-Referenzen | None |
| Secrets/env vars | docker-compose.yml hat hardcoded Fallback-Token für ORG 2596 (Z. 15) | Fallback entfernen, echten Token als Env-Var setzen |
| Build artifacts | Kein egg-info, kein compiled binary | None |

**Token-Rotations-Reihenfolge ist kritisch:**
1. Erst neuen Code deployen (env-var-basiert, ohne hardcoded Fallbacks)
2. Dann auf ChurchDesk-Seite alle 5 API-Tokens rotieren
3. Neue Tokens als Env-Vars auf Server setzen
4. Container neu starten

**Nicht in dieser Reihenfolge → Downtime zwischen alten und neuen Tokens.**

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Secrets im Code | Env-Vars | Python-Standard seit Jahren | Pflicht für alle produktiven Deployments |
| Globales Dict mit Tokens | Config-Modul mit Env-Var-Loading | Best Practice seit 12-Factor-App | Keine Credentials im Repo |

## Open Questions

1. **Standalone-Script-Zukunft**
   - What we know: `gottesdienst_formatter_final.py` ist CLI-Tool im Root, dupilziert Logik aus `web/`
   - What's unclear: Wird es noch aktiv genutzt? CLAUDE.md erwähnt nur den Web-Einsatz
   - Recommendation: In Phase 1 den Import umbiegen (sys.path-Trick). Deprecation-Entscheidung in Phase 2 oder 3 treffen.

2. **index.html — Org-Checkboxen hardcoded**
   - What we know: `index.html` hat hardcoded Checkboxen für die 5 bekannten Orgs (basierend auf STRUCTURE.md)
   - What's unclear: Exaktes Template nicht eingelesen — muss beim Plan-Schritt geprüft werden
   - Recommendation: Beim Plan dynamisches Rendering via `organizations`-Context-Variable einplanen

## Sources

### Primary (HIGH confidence)
- Direkter Code-Read `web/churchdesk_api.py` — Tokens Z. 15-41, format_boyens_pastor Z. 358-422, ORGANIZATIONS-Dict vollständig inventarisiert
- Direkter Code-Read `web/app.py` — secret_key Z. 19, format_pastor Z. 103-125, format_service_type Z. 71-101
- Direkter Code-Read `gottesdienst_formatter_final.py` — Formatierungsfunktionen Z. 18-114
- Direkter Code-Read `web/docker-compose.yml` — hardcoded Token-Fallback Z. 15

### Secondary (MEDIUM confidence)
- `.planning/codebase/CONCERNS.md` — Codebase-Analyse vom 2026-03-21, bestätigt alle Befunde

## Metadata

**Confidence breakdown:**
- Security issues (SEC-01/02): HIGH — direkt im Code verifiziert, Zeilen angegeben
- Code duplication (CODE-01/02/03): HIGH — alle drei Dateien gelesen und verglichen
- Config-driven orgs (CODE-04): HIGH — ORGANIZATIONS-Dict und index.html-Struktur bekannt; Template nicht vollständig gelesen (Open Question 2)
- Refactoring patterns: HIGH — Standard Python-Patterns, keine externe Bibliothek nötig

**Research date:** 2026-03-21
**Valid until:** Unbegrenzt — rein interner Code, kein externer API-Versionsdrift relevant
