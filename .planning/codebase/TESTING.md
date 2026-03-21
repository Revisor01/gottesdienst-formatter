# Testing Patterns

**Analysis Date:** 2026-03-21

## Test Framework

**Status:**
- No automated test framework detected
- No test runner configuration (no `pytest.ini`, `conftest.py`, `unittest.cfg`)
- No test files found in codebase (no `test_*.py`, `*_test.py`, `*_spec.py`)
- Testing approach: manual with sample Excel files

**Manual Testing Approach:**
- Sample Excel file used: `2025-05-20 Gottesdienste 06[1].xlsx`
- Output verified manually: `gottesdienste_formatiert.txt`
- Web interface tested via Flask development server
- ChurchDesk API integration tested with live API calls

## Testing Strategy by Component

### Standalone Script Testing

**File:** `gottesdienst_formatter_final.py`

**Test Approach:**
1. User places Excel file in project directory
2. Script auto-detects `.xlsx` files
3. If multiple files found, user selects via command-line input (lines 125-137)
4. Output previewed to console (first 20 lines) before file save
5. Results saved to `gottesdienste_formatiert.txt`

**Verification Steps (as documented in CLAUDE.md):**
```
1. Use sample Excel files from the project
2. Verify output format matches Boyens Medien requirements
3. Check German date/time formatting
4. Validate service type abbreviations
```

**Excel Data Requirements:**
- Required columns: `Startdatum`, `Titel`, `Standortnamen`, `Mitwirkender`, `Gemeinden`
- Column validation in `app.py` lines 133-136
- Missing columns raise `ValueError` with list of missing fields

### Web Interface Testing

**File:** `web/app.py`

**Routes Tested Manually:**
- `GET /` - Index page load
- `POST /upload` - File upload with validation
  - Extension validation: `file.filename.endswith('.xlsx')` (line 186)
  - Filename validation: empty filename check (lines 182-184)
  - Error cases: missing file, wrong extension, processing errors
- `POST /download` - Text file download
  - Error case: no formatted_text provided
- `POST /fetch_churchdesk_events` - Multi-org API fetch
  - Validation: at least one organization selected
  - Error handling: individual org failures don't break others
- `POST /export_selected_events` - Event filtering and export

**Error Paths:**
- File upload errors handled with try-except wrapping `process_excel_file()` (lines 187-204)
- ChurchDesk API errors caught with `Exception` handler (lines 302-304)
- User feedback via Flask's `flash()` messages

**Data Flow Testing:**
1. Upload → Temporary file creation (tempfile.NamedTemporaryFile)
2. Process → Validation → Pandas DataFrame operations
3. Download → BytesIO serialization for HTTP response
4. ChurchDesk → Multi-org client fetches → JSON serialization for form submission

### ChurchDesk API Testing

**File:** `web/churchdesk_api.py`

**API Client Methods:**
- `_make_request()` (lines 53-70): HTTP request with auth
  - Error handling: `requests.exceptions.RequestException` caught and re-raised
  - Validation: `response.raise_for_status()` for HTTP errors
- `get_event_categories()`: Fetch available categories
- `get_gottesdienst_category_id()`: Filter for Gottesdienst category
  - Cache: result stored in `_gottesdienst_category_id` to avoid repeated API calls
- `get_monthly_events()`: Calculate date range and fetch events

**Multi-Organization Testing:**
- `MultiOrganizationChurchDeskAPI.get_all_events()` (lines 458-492)
  - Tests all 5 organizations sequentially
  - Individual org failures logged but don't stop process (line 486-488)
  - Returns partial results on error

**Test Configuration:**
- 5 test organizations defined in `ORGANIZATIONS` dict (lines 15-41)
- Real API tokens embedded in code
- Development testing against live ChurchDesk API

**Data Transformation Testing:**
- `EventAnalyzer.format_event_for_boyens()` (lines 204-245)
  - Timezone conversion: UTC → German time (CET/CEST)
  - Location extraction with fallbacks
  - Completeness analysis
- `extract_boyens_location()` (lines 248-355)
  - Multiple location format handling
  - Multi-church city logic (Heide, Büsum, Brunsbüttel)
  - Location mapping with separate rules for display vs export
- `format_boyens_pastor()` (lines 358-422)
  - Multiple delimiter handling (`,`, `&`, `und`, `+`, `/`)
  - Prefix detection and normalization
  - Special cases (Kirchspiel-Pastor:innen, Konfirmand:innen)

## Test Data

### Sample Data Sources

**Excel Files:**
- Location: `/Users/simonluthe/Documents/kk-termine/`
- File: `2025-05-20 Gottesdienste 06[1].xlsx`
- Columns: `Startdatum`, `Titel`, `Standortnamen`, `Mitwirkender`, `Gemeinden`

**ChurchDesk API:**
- 5 organizations configured (see `ORGANIZATIONS` dict)
- Real event data fetched from API
- Test data includes various event types: Gottesdienst, Taufe, Konfirmation, Tauffest

### Test Scenarios

**Date Formatting:**
- German weekday names: Montag, Dienstag, Mittwoch, Donnerstag, Freitag, Sonnabend, Sonntag
- German month names: Januar, Februar, März, etc.
- Format: "Sonnabend, 5. April"
- Time format: "9.30 Uhr" (with minutes only if non-zero)

**Service Type Abbreviations:**
- "gottesdienst" → `Gd.`
- "abendmahl" → `Gd. m. A.`
- "taufe" → `Gd. m. T.`
- "konfirmation" → `Konfirmation`
- "tauffest" → `Tauffest`
- "kinderkirche" → `Kinderkirche`
- "familiengottesdienst" → `Familiengd.`
- "andacht" → `Andacht`
- "abendsegen" → `Abendsegen`

**Pastor Name Formatting:**
- Input: "Pastor Schmidt" → Output: "P. Schmidt"
- Input: "Pastorin Müller" → Output: "Pn. Müller"
- Input: "Diakon Weber" → Output: "D. Weber"
- Input: "Diakonin König" → Output: "Dn. König"
- Multiple: "Pastor Schmidt & Pastorin Müller" → "P. Schmidt & Pn. Müller"

**Location Mapping (Büsum):**
- "Büsum | St. Clemens" → `Büsum` (main church = just city)
- "Büsum | Perlebucht" → `Büsum, Perlebucht`
- Export: "Urlauberseelsorge" → `Büsum`
- Display: "Urlauberseelsorge" → `Urlauberseelsorge`

## Validation Testing

**Input Validation:**
- Excel column requirement check: `missing_columns` validation (app.py lines 134-136)
- File extension check: `.xlsx` required (app.py line 186)
- Organization selection: at least one required (app.py lines 243-245)
- Date format: ISO format for ChurchDesk events (app.py line 348)

**Data Validation:**
- Empty/NaN handling: `pd.isna()` checks throughout format functions
- String trimming: `.strip()` applied to name inputs
- None/empty string defaults: most format functions return empty string on missing data

## Error Cases Tested

**File Upload Errors:**
1. No file submitted → Flash "Keine Datei ausgewählt" (line 178)
2. Empty filename → Flash "Keine Datei ausgewählt" (line 183)
3. Non-Excel file → Flash "Bitte wählen Sie eine Excel-Datei (.xlsx) aus" (line 206)
4. Excel read failure → Propagates as ValueError for missing columns
5. Processing exception → Flash "Fehler beim Verarbeiten der Datei: {error}" (line 203)

**ChurchDesk API Errors:**
1. Individual org fails → Logged and skipped, other orgs continue (line 487)
2. API authentication fails → Raised as Exception with error message (line 70)
3. Network error → Caught as `RequestException` and wrapped (line 69)

**Data Edge Cases:**
- Missing `Startdatum` field → Skipped from EventAnalyzer output (lines 213-214)
- Missing pastor name → Returns empty string, not appended to output (app.py line 167)
- Missing location → Falls back to parish name (app.py line 160)
- Unrecognized service type → Default to "Gd." (app.py line 101)

## Output Verification

**Text Format Output:**
```
Sonnabend, 5. April:
Büsum: 9.30 Uhr, Gd. m. A., P. Schmidt
Heide: 11.00 Uhr, Gd., Pn. Müller

Sonntag, 6. April:
Lunden: 10.00 Uhr, Gd., P. Weber
```

**Requirements:**
1. Chronological date ordering (sorted by Startdatum)
2. Within each date, entries in event order
3. Location formatted per Boyens Media rules
4. Time in format "H.MM Uhr" (minutes omitted if zero)
5. Service type abbreviations applied
6. Pastor names prefixed with P./Pn./D./Dn.
7. Blank line after each date

## Known Testing Gaps

1. **No unit tests:** All formatting functions lack isolated test cases
2. **No integration tests:** Full workflows only tested manually
3. **No timezone tests:** Edge cases around DST transitions not covered
4. **No performance tests:** No benchmarks for large Excel files or many organizations
5. **No security tests:** No SQL injection, XSS, or upload vulnerability testing
6. **No API response variation:** Assumes consistent ChurchDesk API response format
7. **No Excel format variation:** Only tested with current column structure
8. **No multi-threading tests:** Concurrent upload scenarios untested
9. **No Docker tests:** Docker image build/run not validated in pipeline

## Testing Best Practices to Implement

1. **Unit Test Suite:**
   - Test each format_* function with edge cases
   - Test location mapping comprehensively
   - Mock ChurchDesk API responses
   - Location: `tests/test_churchdesk_api.py`, `tests/test_app.py`

2. **Fixture Setup:**
   - Create sample Excel file with all test cases
   - Create mock ChurchDesk API responses (JSON files)
   - Location: `tests/fixtures/`

3. **Test Runner:**
   - Use pytest for Python testing
   - Config file: `pytest.ini` or `setup.cfg`
   - Run via: `pytest tests/`

4. **Coverage Target:**
   - Aim for 80%+ coverage on core formatting functions
   - Location: `.coverage` output or `htmlcov/`

---

*Testing analysis: 2026-03-21*
