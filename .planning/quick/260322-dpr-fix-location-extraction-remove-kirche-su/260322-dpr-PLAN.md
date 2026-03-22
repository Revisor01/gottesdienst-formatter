---
phase: quick
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - web/churchdesk_api.py
  - web/formatting.py
  - web/tests/test_formatting.py
autonomous: true
requirements: [LOC-FIX]

must_haves:
  truths:
    - "Heide St.-Juergen-Kirche wird zu 'Heide, St.-Juergen' (Komma, ohne -Kirche)"
    - "Einzelkirchen-Orte (Hennstedt, Hemme, Lunden, Weddingstedt, Schlichting, St. Annen) geben nur Ortsnamen zurueck"
    - "Buesum - St. Clemens-Kirche wird zu 'Buesum' (Separator und -Kirche entfernt)"
    - "Heide Erloeskirche/Auferstehungskirche bekommt Komma-Trennung"
    - "Heide-Suederholm bleibt unveraendert (eigener Ort)"
    - "Sonderformat-Titel wie 'Gottesdienst mit Tisch-Abendmahl: ...' werden sinnvoll abgekuerzt"
  artifacts:
    - path: "web/churchdesk_api.py"
      provides: "Erweiterte extract_boyens_location mit Kirche-Suffix-Logik und Separator-Normalisierung"
    - path: "web/formatting.py"
      provides: "format_service_type mit Sonderformat-Handling fuer Kolon-Titel"
    - path: "web/tests/test_formatting.py"
      provides: "Tests fuer alle neuen Location- und Sonderformat-Cases"
  key_links:
    - from: "web/churchdesk_api.py"
      to: "web/app.py"
      via: "extract_boyens_location aufgerufen in process_excel_file und convert_churchdesk_events_to_boyens"
      pattern: "extract_boyens_location"
    - from: "web/formatting.py"
      to: "web/app.py"
      via: "format_service_type aufgerufen fuer jeden Termin"
      pattern: "format_service_type"
---

<objective>
Fix location extraction and Sonderformat title handling for Boyens output.

Purpose: Real April 2026 ChurchDesk export produces wrong location names — " Kirche" suffix not stripped, multi-church cities missing comma separator, Buesum uses " - " instead of ", ", and Sonderformat titles bypass abbreviation.

Output: Corrected extract_boyens_location() and format_service_type() with full test coverage for all reported cases.
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@web/churchdesk_api.py (extract_boyens_location — main fix target, lines 221-335)
@web/formatting.py (format_service_type — Sonderformat handling, lines 48-99)
@web/tests/test_formatting.py (existing tests to extend)
@web/app.py (consumers of both functions — read-only context)
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add test cases for all broken location extractions and Sonderformat titles</name>
  <files>web/tests/test_formatting.py</files>
  <behavior>
    Location extraction (extract_boyens_location, for_export=True):
    - "Heide St.-Jürgen-Kirche" → "Heide, St.-Jürgen"
    - "Hennstedt Kirche" → "Hennstedt"
    - "Hemme Kirche" → "Hemme"
    - "Lunden Kirche" → "Lunden"
    - "Weddingstedt Kirche" → "Weddingstedt"
    - "Schlichting Kirche" → "Schlichting"
    - "St. Annen Kirche" → "St. Annen"
    - "Büsum - St. Clemens-Kirche" → "Büsum" (St. Clemens = Hauptkirche)
    - "Büsum - Perlebucht" → "Büsum, Perlebucht"
    - "Heide Erlöserkirche" → "Heide, Erlöserkirche"
    - "Heide Auferstehungskirche" → "Heide, Auferstehungskirche"
    - "Heide-Süderholm" → "Heide-Süderholm" (eigener Ort, nicht splitten)
    - Existing pipe/comma cases still pass

    Sonderformat titles (format_service_type):
    - "Gottesdienst mit Tisch-Abendmahl: Brot des Lebens" → "Gd. m. A." (Kolon-Teil abschneiden, Abendmahl erkennen)
    - "Gottesdienst zum Karfreitag mit Abendmahl" → "Gd. m. A." (mit-Praeposition kein Problem, Abendmahl wird erkannt)
    - "Gottesdienst zum Ostersonntag" → "Gd." (kein Sondertyp, normaler Gd.)
  </behavior>
  <action>
    Import extract_boyens_location from churchdesk_api in test_formatting.py.
    Add parametrized test_extract_boyens_location with all cases listed above (for_export=True).
    Add parametrized test_extract_boyens_location_display with Buesum display cases (for_export=False): "Büsum - St. Clemens-Kirche" → "Urlauberseelsorge" should NOT apply (St. Clemens is NOT Urlauberseelsorge); keep existing Urlauberseelsorge mapping tests.
    Add parametrized test_format_service_type_sonderformat with Kolon-Titel cases.
    Run tests — they MUST fail (RED phase).
  </action>
  <verify>
    <automated>cd /Users/simonluthe/Documents/kk-termine/web && python -m pytest tests/test_formatting.py -x --tb=short 2>&1 | tail -20</automated>
  </verify>
  <done>All new test cases exist and fail against current code (RED). Existing tests still pass.</done>
</task>

<task type="auto">
  <name>Task 2: Fix extract_boyens_location and format_service_type to pass all tests</name>
  <files>web/churchdesk_api.py, web/formatting.py</files>
  <action>
    **web/churchdesk_api.py — extract_boyens_location():**

    The core problem: ChurchDesk returns location strings WITHOUT separators, e.g. "Hennstedt Kirche", "Heide St.-Jürgen-Kirche", "Büsum - St. Clemens-Kirche". The current code only handles pipe (" | ") and comma (", ") separators, so these fall through to the LOCATION_MAPPINGS dict (which only matches exact church names like "st. secundus-kirche", not "Hennstedt Kirche").

    Add a new processing block BEFORE the "No separator found" section (before line 297) to handle these patterns:

    1. **Dash separator "Ort - Kirche"**: Normalize "Büsum - St. Clemens-Kirche" by splitting on " - ", then process like pipe separator. Apply same Büsum/Heide/Brunsbüttel logic. Strip "-Kirche" suffix from church part.

    2. **"Ort Kirche" pattern (single-church towns)**: After all separator checks, if location ends with " Kirche", strip it. This handles Hennstedt Kirche → Hennstedt, Hemme Kirche → Hemme, etc. But FIRST check if the word before " Kirche" belongs to a multi-church city — if so, treat the preceding word as city and remaining as church name.

    3. **Multi-church city detection without separator**: For Heide specifically — if location starts with "Heide " and does NOT contain a separator, treat everything after "Heide " as church name. Examples: "Heide St.-Jürgen-Kirche" → city="Heide", church="St.-Jürgen-Kirche" → strip "-Kirche" → "Heide, St.-Jürgen". "Heide Erlöserkirche" → "Heide, Erlöserkirche". "Heide Auferstehungskirche" → "Heide, Auferstehungskirche".

    4. **Heide-Süderholm**: Must NOT be split. Check: if location starts with "Heide-" (hyphen, not space), leave as-is. This check must come BEFORE the "Heide " prefix check.

    5. **Strip "-Kirche" suffix generically** from church part in multi-church cities (already done for pipe/comma Heide cases, extend to new patterns). Also strip " Kirche" (space) suffix when detected at end of church name.

    Concrete implementation approach — add this block after the comma-separator block (line 295) and before the "No separator found" comment (line 297):

    ```python
    # Handle dash separator: "Büsum - St. Clemens-Kirche"
    if ' - ' in location:
        parts = location.split(' - ', 1)
        city = parts[0].strip()
        church = parts[1].strip()
        # Strip -Kirche / -kirche suffix from church
        if church.endswith('-Kirche') or church.endswith('-kirche'):
            church = church[:-len('-Kirche')]
        # Apply same multi-church logic as pipe separator
        city_lower = city.lower()
        if city_lower == 'büsum':
            if 'st. clemens' in church.lower():
                return "Büsum" if for_export else "Büsum"
            elif 'perlebucht' in church.lower():
                return "Büsum, Perlebucht"
            else:
                return f"Büsum, {church}"
        elif any(mc in city_lower for mc in MULTI_CHURCH_CITIES):
            return f"{city}, {church}"
        else:
            return city

    # Handle "Ort Kirche" without separator — detect multi-church cities first
    # Heide-Süderholm: hyphenated compound → leave as-is (own Ort)
    # Heide + church: "Heide St.-Jürgen-Kirche", "Heide Erlöserkirche"
    for multi_city in MULTI_CHURCH_CITIES:
        # Match "City Church..." where City is a multi-church city
        # But NOT "City-Something" (hyphenated compounds like Heide-Süderholm)
        if location_lower.startswith(multi_city + ' ') and not location_lower.startswith(multi_city + '-'):
            city = location[:len(multi_city)]
            # Capitalize city properly from original
            church = location[len(multi_city)+1:].strip()
            # Strip -Kirche / -kirche suffix
            if church.endswith('-Kirche') or church.endswith('-kirche'):
                church = church[:-len('-Kirche')]
            if church.endswith(' Kirche') or church.endswith(' kirche'):
                church = church[:-len(' Kirche')]
            # Apply city-specific logic
            city_cap = location[:len(multi_city)]  # preserve original casing
            city_lower_val = city_cap.lower()
            if city_lower_val == 'büsum':
                if 'st. clemens' in church.lower():
                    return "Büsum" if for_export else "Büsum"
                elif 'perlebucht' in church.lower():
                    return "Büsum, Perlebucht"
                else:
                    return f"Büsum, {church}"
            else:
                return f"{city_cap}, {church}"

    # Single-church towns: strip trailing " Kirche"
    if location.endswith(' Kirche') or location.endswith(' kirche'):
        return location[:-len(' Kirche')].strip()
    ```

    **web/formatting.py — format_service_type():**

    Add handling for titles with colon BEFORE the existing checks (after the Sonderformat/Anfuehrungszeichen check at line 56, before 'tauffest' check at line 59):

    ```python
    # Kolon-Titel: "Gottesdienst mit Tisch-Abendmahl: Brot des Lebens"
    # Schneide den Teil nach dem Kolon ab, dann normal weiter
    if ':' in titel and '„' not in titel:
        titel_before_colon = titel.split(':', 1)[0].strip()
        titel_lower = titel_before_colon.lower()
        # Fall through to normal checks with truncated title
    ```

    This reassigns titel_lower so subsequent checks (abendmahl, tauf, etc.) match on the part before the colon. The "zum Karfreitag mit Abendmahl" case already works because "abendmahl" is in the full titel_lower — no change needed there.

    IMPORTANT: Do NOT change behavior for titles with Anfuehrungszeichen (already handled at line 56). Only apply colon-truncation when no quote marks present.
  </action>
  <verify>
    <automated>cd /Users/simonluthe/Documents/kk-termine/web && python -m pytest tests/test_formatting.py -v --tb=short 2>&1 | tail -40</automated>
  </verify>
  <done>All tests pass (GREEN). Location names match Boyens expectations: single-church towns show only town name, multi-church cities show "City, Church", Kirche suffix removed, Sonderformat titles abbreviated correctly.</done>
</task>

</tasks>

<verification>
1. All existing tests in test_formatting.py still pass (no regressions)
2. All new parametrized location test cases pass
3. All new Sonderformat test cases pass
4. Goldstandard test (test_boyens_goldstandard.py) still passes if it exists
</verification>

<success_criteria>
- extract_boyens_location("Heide St.-Jürgen-Kirche") == "Heide, St.-Jürgen"
- extract_boyens_location("Hennstedt Kirche") == "Hennstedt"
- extract_boyens_location("Büsum - St. Clemens-Kirche") == "Büsum"
- extract_boyens_location("Heide Erlöserkirche") == "Heide, Erlöserkirche"
- extract_boyens_location("Heide-Süderholm") == "Heide-Süderholm"
- format_service_type("Gottesdienst mit Tisch-Abendmahl: Brot des Lebens") == "Gd. m. A."
- Full test suite green
</success_criteria>

<output>
After completion, create `.planning/quick/260322-dpr-fix-location-extraction-remove-kirche-su/260322-dpr-SUMMARY.md`
</output>
