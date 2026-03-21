# Codebase Concerns

**Analysis Date:** 2025-03-21

## Security Issues

**Hardcoded API Tokens in Source Code:**
- Issue: ChurchDesk API tokens embedded directly in `ORGANIZATIONS` dict in `web/churchdesk_api.py` (lines 15-41)
- Files: `web/churchdesk_api.py` (lines 15-41)
- Risk: API credentials exposed in version control history. Any compromise of the repository exposes all 5 church organization API tokens.
- Current mitigation: `.env` variables available but not enforced; tokens are hardcoded as fallback
- Recommendations:
  1. Remove all tokens from source code immediately
  2. Mandate environment variables: `CHURCHDESK_ORG_{ORG_ID}_TOKEN`
  3. Update `docker-compose.yml` to require token injection at deployment time
  4. Rotate all API tokens (assume compromised since they're in git history)

**Flask Secret Key is Hardcoded:**
- Issue: `app.secret_key = 'gottesdienst-formatter-secret-key'` in `web/app.py` (line 19)
- Files: `web/app.py` (line 19)
- Risk: Session/CSRF token generation is predictable; compromises session security
- Recommendations: Load from environment variable with secure generation fallback

**No Input Validation on File Uploads:**
- Issue: File upload endpoint (`/upload` in `web/app.py` line 175-207) only checks filename extension
- Files: `web/app.py` (lines 175-207)
- Risk: Can upload arbitrary files with `.xlsx` extension. No validation of file contents, size limits, or MIME type verification
- Safe modification: Add file size limit, validate actual Excel file structure via `openpyxl`, implement virus scanning for production

## Code Duplication & Maintainability

**Date/Time Formatting Duplicated Across Three Files:**
- Issue: `format_date()`, `format_time()`, and `format_service_type()` functions are identical or nearly identical in both scripts
- Files:
  - `gottesdienst_formatter_final.py` (lines 18-86)
  - `web/app.py` (lines 36-101)
- Impact: Changes to formatting rules must be made in multiple places; risk of inconsistency
- Fix approach: Extract shared formatting logic to `web/shared.py` or `formatting.py`, import in both scripts and web app

**Pastor Formatting Logic Duplicated:**
- Issue: `format_pastor()` function exists in two places with slightly different logic
- Files:
  - `gottesdienst_formatter_final.py` (lines 88-114)
  - `web/app.py` (lines 103-125)
- Plus a third variant: `format_boyens_pastor()` in `web/churchdesk_api.py` (lines 358-422)
- Impact: Three different pastor formatting implementations create inconsistent output
- Fix approach: Consolidate to single `format_boyens_pastor()` function used everywhere

## Testing Coverage Gaps

**No Automated Tests:**
- What's not tested: All core formatting functions (`format_date`, `format_time`, `format_service_type`, `format_pastor`)
- Files: All `.py` files lack test files
- Risk: Regressions go undetected. German date formatting, service type mappings, and pastor title conversions cannot be validated
- Priority: High - location mapping changes (Büsum, Urlauberseelsorge) are fragile without tests

**No Validation of API Response Handling:**
- What's not tested: `EventAnalyzer.format_event_for_boyens()` function with various malformed inputs
- Files: `web/churchdesk_api.py` (lines 204-245)
- Risk: Missing fields in ChurchDesk API responses could cause silent failures or incorrect output
- Priority: High - production API calls will encounter edge cases not covered

**No Integration Tests for File Processing:**
- What's not tested: End-to-end Excel upload → formatting → download workflow
- Files: `web/app.py` (upload/download endpoints)
- Risk: Breaking changes to pandas column handling or file I/O errors discovered in production
- Priority: Medium

## Fragile Areas

**Location Mapping Logic:**
- Files: `web/churchdesk_api.py` (lines 248-355), `extract_boyens_location()` function
- Why fragile: Complex nested conditionals with display vs export variants (lines 320-354). Multi-church city detection hardcoded as list (line 259)
- Current issues: Büsum mapping just underwent a fix (commit cd642a2), Urlauberseelsorge requires different output for display vs export (lines 347-348)
- Safe modification:
  1. Extract multi-city list to module constant
  2. Create location mapping test fixtures with known good outputs
  3. Document why Büsum, Heide, Brunsbüttel need special handling
  4. Add warning comments for Urlauberseelsorge → Büsum export rule

**Event Completeness Analysis Assumes Field Structure:**
- Files: `web/churchdesk_api.py` (lines 162-201), `EventAnalyzer.analyze_event_completeness()`
- Why fragile: Assumes specific field names (`title`, `startDate`, `location`, `contributor`, `parishes`). If ChurchDesk API changes field names/structure, parsing silently produces incomplete results
- Safe modification: Add logging when required fields are missing, validate API response structure before processing

**Pastor Prefix Detection Based on String Matching:**
- Files: `web/churchdesk_api.py` (lines 358-422), `format_boyens_pastor()`
- Why fragile: Uses naive substring matching (`'pastor' in contrib_lower`) which will match "Pastor Müller" correctly but also match unintended strings. No word boundary checking
- Current risk: "Pastorin" check (line 408) occurs before "Pastor" check (line 410) so order matters
- Safe modification: Use regex with word boundaries or lookup table instead of string matching

**Excel Column Name Dependencies:**
- Files: `web/app.py` (lines 132-136), `gottesdienst_formatter_final.py` (lines 142-162)
- Why fragile: Hardcoded list of required columns with exact names. If Excel file uses different names (e.g., "Start Date" vs "Startdatum"), fails with cryptic error
- Impact: User-facing error: "Fehlende Spalten: Startdatum, ..."
- Safe modification: Add fuzzy column matching or create column mapping UI, provide better error messages suggesting correct column names

## Performance Bottlenecks

**No Pagination for API Requests:**
- Problem: `MultiOrganizationChurchDeskAPI.get_all_events()` (lines 458-492) fetches all events for month without pagination
- Files: `web/churchdesk_api.py` (lines 458-492)
- Cause: Single API call per organization gets up to 100 items (hardcoded in line 99). If month has >100 services, only first 100 returned
- Impact: Large churches/months would silently miss events
- Improvement path: Implement pagination loop, detect `itemsNumber` in response to know if more pages exist

**Excel Processing Loads Entire File to Memory:**
- Problem: `process_excel_file()` reads entire Excel file with `pd.read_excel()` without chunking
- Files: `web/app.py` (line 130)
- Impact: Large Excel files (>10MB) could cause memory issues in container with limited resources
- Improvement path: For simple formatting, stream process or validate file size upfront

## Tech Debt

**Dual Implementation Maintenance Burden:**
- Issue: Two independent scripts solve same problem: `gottesdienst_formatter_final.py` (standalone CLI) and `web/app.py` (Flask web app)
- Files: Root-level `gottesdienst_formatter_final.py` vs `web/app.py`
- Impact: Bug fixes or feature additions must be made in both places. CLAUDE.md doesn't explain when to use which script
- Fix approach:
  1. Deprecate standalone script, move logic to web app
  2. Provide CLI wrapper that uses Flask app backend
  3. Or clearly document that standalone script is legacy only

**No Configuration File Support:**
- Issue: All configuration hardcoded or in environment variables only
- Files: `web/churchdesk_api.py` (ORGANIZATIONS dict), `web/app.py` (secret_key)
- Impact: Cannot easily customize behavior without code changes
- Recommendations: Implement config.yaml with organization definitions, location mappings, service type rules

**Inconsistent Error Handling:**
- Issue: Some functions return `None` on error (e.g., `EventAnalyzer.format_event_for_boyens()` line 245), others raise exceptions
- Files: `web/churchdesk_api.py` (lines 204-245), `web/app.py` (lines 127-169)
- Impact: Inconsistent error propagation; some failures logged, others silently ignored
- Fix approach: Define error handling strategy: fail-fast with exceptions or graceful degradation with None returns?

## Missing Critical Features

**No Undo/Recovery for Exports:**
- Problem: Once events exported and user downloads file, no way to recover if export was incorrect
- Impact: User must manually fix output or re-run export
- Blocks: Safe production use without validation step

**No Audit Logging:**
- Problem: No record of what was exported, when, by whom, or from which organizations
- Files: All files lack logging infrastructure
- Impact: Cannot debug production issues or audit data exports
- Blocks: Compliance requirements, troubleshooting user-reported issues

**No Caching of API Responses:**
- Problem: Every fetch of the same month re-queries ChurchDesk API
- Files: `web/churchdesk_api.py` (no caching logic)
- Impact: Slow repeated loads, puts load on ChurchDesk API, potential rate limiting
- Improvement: Implement Redis cache with 1-day TTL for monthly event queries

## Dependencies at Risk

**Flask 2.3.3 and Werkzeug 2.3.7 (Older Versions):**
- Risk: Both packages are 2 years old (published ~2023). No active vulnerability checking documented
- Files: `web/requirements.txt` (lines 1, 4)
- Impact: Known security vulnerabilities may exist
- Migration plan: Upgrade to Flask 3.x (requires minimal code changes), Werkzeug 3.x

**Pandas 2.3.1 (Outdated):**
- Risk: Current version is 3.0+; this is significantly behind
- Files: `web/requirements.txt` (line 2)
- Impact: Missing performance improvements, bug fixes
- Migration plan: Test upgrade to latest 3.x; likely compatible with current usage

**No Requirements Pinning Strategy:**
- Risk: All dependencies use exact versions but no hash verification or lock file (like `poetry.lock` or `pip-compile`)
- Files: `web/requirements.txt` has no hashes
- Impact: Reproducibility issues, potential pip package substitution attacks
- Recommendation: Use `pip-tools` or `poetry` for lock file generation

## Known Bugs & Inconsistencies

**Büsum Location Mapping in Flux:**
- Symptom: Recent commits show changes to Büsum handling (cd642a2, f411d57)
- Files: `web/churchdesk_api.py` (lines 273-280, 301-307)
- Current state: St. Clemens returns just "Büsum", but business rule documentation in CLAUDE.md says should use "Urlauberseelsorge" in overview and "Büsum" in export
- Current code: Uses "Urlauberseelsorge" for display (line 348) but export rule maps to "Büsum" (line 333)
- Workaround: Follow export behavior; display uses location mapping with `for_export=False` flag
- Risk: Next developer may not understand the distinction and break it again

**Month Selection Limited to Current/Future:**
- Problem: No UI control for past months; API fetch endpoint accepts any year/month but UI may not provide them
- Files: `web/templates/churchdesk_events.html` not examined but implied by form structure
- Impact: Users cannot export historical services for re-publication or verification
- Fix: Add month/year picker to UI, document past month support in API

**No Error Messages for API Failures:**
- Problem: `MultiOrganizationChurchDeskAPI.get_all_events()` silently skips organizations on error (line 487: `continue`)
- Files: `web/churchdesk_api.py` (lines 486-488)
- Impact: User doesn't know if events were missing because org had no services or because API failed
- Fix: Track failed orgs, display warning message

## Scaling Limits

**Single ChurchDesk API Token per Organization:**
- Current capacity: 5 organizations with hardcoded tokens
- Limit: Adding new organizations requires code change
- Scaling path: Move organization config to database, allow admin UI for adding new organizations

**Container Resource Limits Not Defined:**
- Problem: `docker-compose.yml` has no memory/CPU limits
- Files: `web/docker-compose.yml`
- Impact: Excel processing could consume all available RAM, crash container
- Fix: Add `mem_limit: 512m`, `memswap_limit: 1g` to docker-compose.yml

**Port Mapping Hardcoded:**
- Problem: Port 5001 hardcoded in docker-compose.yml (line 8)
- Impact: Cannot run multiple instances on same server
- Fix: Use environment variable `${CONTAINER_PORT:-5001}`

## Quality Concerns

**No Type Hints:**
- Issue: Functions in Python files use no type hints (PEP 484)
- Files: All `.py` files
- Impact: IDE autocomplete reduced, harder to catch bugs, code intent unclear
- Priority: Low (refactoring only, no functionality change)

**Magic Numbers and Strings:**
- Issue: Hardcoded values scattered throughout code
- Examples:
  - Month map (line 49-53 in multiple files)
  - Service type abbreviations (line 60-67 in formatter_final.py)
  - Organization IDs (line 15-41 in churchdesk_api.py)
- Fix: Extract to module-level constants

**Inconsistent Docstrings:**
- Issue: Some functions have detailed docstrings, others have none
- Files: Functions in `churchdesk_api.py` are well-documented, but `format_date()` in multiple files lack parameter documentation
- Impact: Makes API harder to understand

---

*Concerns audit: 2025-03-21*
