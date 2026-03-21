# Coding Conventions

**Analysis Date:** 2026-03-21

## Naming Patterns

**Files:**
- Python scripts: `lowercase_with_underscores.py` (e.g., `gottesdienst_formatter_final.py`, `churchdesk_api.py`)
- Template files: `lowercase.html` (e.g., `index.html`, `churchdesk_events.html`)
- Class names in PascalCase (e.g., `ChurchDeskAPI`, `EventAnalyzer`, `MultiOrganizationChurchDeskAPI`)

**Functions:**
- Utility functions: `snake_case` (e.g., `format_date()`, `format_time()`, `format_service_type()`)
- Descriptive names reflecting purpose: `format_pastor()`, `process_excel_file()`, `extract_boyens_location()`
- Internal helper functions prefixed with underscore: `_make_request()`, `_gottesdienst_category_id`

**Variables:**
- Local variables: `snake_case` (e.g., `output_lines`, `formatted_text`, `selected_orgs`)
- Boolean flags: descriptive `is_*` or `for_*` prefix (e.g., `for_export`, `gottesdienst_only`)
- Collections: plural names (e.g., `events`, `contributors`, `missing_fields`, `formatted_contributors`)

**Types:**
- Constants: `UPPERCASE` (e.g., `ORGANIZATIONS`, `MULTI_CHURCH_CITIES`, `LOCATION_MAPPINGS`)
- Type hints used in function signatures (e.g., `str`, `Dict`, `List`, `Optional`)
- Dictionary keys: `snake_case` strings

**Module Level:**
- Module docstrings at top with UTF-8 encoding declaration: `#!/usr/bin/env python3` and `# -*- coding: utf-8 -*-`
- Imports organized: standard library first, then third-party packages
- Global configuration (e.g., `ORGANIZATIONS` dict) declared at module level in `churchdesk_api.py`

## Code Style

**Formatting:**
- No automated formatter detected (no `.prettierrc` or `pylint` config)
- String formatting: use `.format()` method exclusively (not f-strings)
  - Example: `"{}: {}".format(ort, zeit)` not `f"{ort}: {zeit}"`
- Indentation: 4 spaces (Python standard)
- Line length: appears to follow implicit ~80-100 character limit
- File encoding: UTF-8 explicit declaration in headers

**Linting:**
- No `.eslintrc`, `pylint.ini`, or equivalent configuration found
- No pre-commit hooks or automated linting detected
- Code style enforced manually through peer review

**Code Structure:**
- Docstrings present for public functions (e.g., `"""Fetch events from ChurchDesk API""")
- Type hints in function signatures: `def __init__(self, api_token: str, organization_id: int)`
- Comments explain complex logic (e.g., location mapping rules for Büsum churches)

## Import Organization

**Order:**
1. Standard library imports (`import pandas as pd`, `import sys`, `from datetime import datetime`)
2. Third-party packages (`import requests`, `import pytz`, `from flask import Flask`)
3. Local imports (`from churchdesk_api import ChurchDeskAPI`)

**Style:**
- Imports at top of file (not inline)
- Use `from X import Y` for clarity rather than `import X as X`
- No wildcard imports (`from X import *`)

**Path Aliases:**
- No path aliases detected (no `jsconfig.json` or `tsconfig.json` for Python)
- Relative imports used in Flask app (e.g., `from churchdesk_api import ...`)

## Error Handling

**Patterns:**
- Try-except blocks with specific exception types when possible
- Example from `app.py`: catches `ValueError` for column validation
- Generic exception handling with message pass-through: `except Exception as e: raise Exception("Message: {}".format(str(e)))`
- Error messages include context about what failed
- ChurchDesk API errors: `except requests.exceptions.RequestException as e: raise Exception(f"ChurchDesk API Error: {str(e)}")`

**Error Recovery:**
- In multi-org API client: errors from individual organizations don't stop fetching from others
  - Example: `except Exception as e: print(...); continue` allows partial success
- File upload validation: checks filename extension before processing
- Flask routes use `flash()` to display user-facing error messages

**Fallback Logic:**
- Location extraction has multiple fallback strategies:
  - Try `locationName`, fall back to `location`, then fall back to parish name
  - Multiple separator formats handled (`|` and `,`)
- Excel column availability: uses `not pd.isna()` checks for optional fields
- Missing data handling returns empty string `""` rather than None/Exception

## Logging

**Framework:** `print()` statements (console output only)

**Patterns:**
- Status messages: `print("Verwende Datei: {}".format(file_path))`
- Error details: traceback via `traceback.print_exc()` in standalone script
- Multi-org API: `print(f"Error fetching events from org {org_id}: {e}")` with continue
- No persistent logging to file detected
- Flask: no request logging configured beyond Flask's default

**Severity Levels:**
- Warnings: printed directly (e.g., "Warnung: Deutsche Lokalisierung nicht verfügbar")
- Errors: printed before raising exception or returning

## Comments

**When to Comment:**
- Complex business logic (e.g., Büsum church location mapping)
- Non-obvious decision points (e.g., why `cid` parameter is used instead of `category_ids`)
- Data transformations that aren't immediately clear

**Style:**
- Inline comments explaining "why" not "what"
- Docstrings for public methods and classes
- German comments mixed with English code

**JSDoc/TSDoc:**
- Not applicable (Python codebase)
- Docstrings use triple-quoted format: `"""Description here"""`
- Parameter documentation in docstrings where present
- Example: `"""Fetch events for specified date range\n\nArgs:\n    start_date: Start date for events..."""`

## Function Design

**Size:**
- Utility functions (format_*): 10-20 lines typical
- API methods: 15-30 lines
- Business logic functions (convert_churchdesk_events_to_boyens): 30-50 lines
- No functions exceed 60 lines observed

**Parameters:**
- Most functions take 1-3 parameters
- Optional parameters passed as keyword args with defaults
- Type hints used: `start_date: datetime`, `category_ids: List[int] = None`
- No parameter validation at function entry (relies on caller correctness)

**Return Values:**
- Functions return data directly (dict, list, string, or None)
- Multiple return values use tuple: not observed
- Void functions return implicitly (None)
- JSON-serializable returns for Flask routes

**Pure Functions:**
- Format functions are pure (same input → same output): `format_date()`, `format_time()`, `format_service_type()`
- Stateful functions: API client methods that maintain session/state
- Side effects: file writing in standalone script, Flask responses with file downloads

## Module Design

**Exports:**
- Public API classes: `ChurchDeskAPI`, `EventAnalyzer`, `MultiOrganizationChurchDeskAPI`
- Helper functions exported: `extract_boyens_location()`, `format_boyens_pastor()`, `create_multi_org_client()`
- Constants exported: `ORGANIZATIONS` dict accessible module-wide

**Barrel Files:**
- Not applicable (no barrel/index files for re-exports)
- Main entry point for web: `app.py` (Flask routes and process functions)
- Main entry point for CLI: `gottesdienst_formatter_final.py`

**Module Responsibilities:**
- `churchdesk_api.py`: ChurchDesk API integration, event formatting, location mapping
- `app.py`: Flask routes, file upload handling, Excel processing, template rendering
- `gottesdienst_formatter_final.py`: Standalone CLI utility with same formatting functions as web version

**Separation of Concerns:**
- API layer separate from formatting layer
- HTML rendering delegated to Jinja2 templates
- Business logic (formatting) separate from HTTP layer (Flask routes)

## German Language

**Conventions:**
- Function names in English (e.g., `format_date()` not `datum_formatieren()`)
- Docstrings in German with English class/module docstrings
- Variable names in English (e.g., `grouped`, `output_lines`, not `gruppiert`, `ausgabezeilen`)
- User-facing strings in German (e.g., "Fehler beim Verarbeiten der Datei")
- Comments mix German and English as appropriate

## Code Examples

**Formatting Pattern:**
```python
def format_pastor(mitwirkender):
    """Formatiert Pastor/Pastorin Namen"""
    if pd.isna(mitwirkender):
        return ""

    name = str(mitwirkender).strip()

    prefixes = ['Pastor ', 'Pastorin ', 'P. ', 'Pn. ', 'Diakon ', 'Prädikant ']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break

    if any(word in mitwirkender.lower() for word in ['pastorin', 'pn.']):
        return "Pn. {}".format(name)
    # ... more conditions
```

**API Client Pattern:**
```python
class ChurchDeskAPI:
    def __init__(self, api_token: str, organization_id: int):
        self.api_token = api_token
        self.organization_id = organization_id
        self.base_url = "https://api2.churchdesk.com/api/v3.0.0"
        self.session = requests.Session()

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        # Private helper method with underscore prefix
```

**Route Handler Pattern:**
```python
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Keine Datei ausgewählt')
        return redirect(request.url)

    try:
        # Business logic
        return render_template('result.html', data=data)
    except Exception as e:
        flash('Fehler: {}'.format(str(e)))
        return redirect(url_for('index'))
```

---

*Convention analysis: 2026-03-21*
