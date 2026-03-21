# Architecture

**Analysis Date:** 2026-03-21

## Pattern Overview

**Overall:** Multi-layer request-response architecture with dual processing paths (Excel upload + ChurchDesk API integration)

**Key Characteristics:**
- Flask-based web application with MVC pattern
- Separation of concerns: API client, data formatting, web interface
- Support for two data sources: Excel files and external ChurchDesk API
- Standardized output formatting for Boyens Media publication requirements
- Single-organization and multi-organization API support

## Layers

**Presentation Layer:**
- Purpose: User-facing web interface for file upload and API interaction
- Location: `web/templates/`, `web/app.py` (routes and request handling)
- Contains: HTML/Jinja2 templates, form handling, result display
- Depends on: Flask framework, formatting functions
- Used by: Web browsers via HTTP/POST requests

**Business Logic Layer:**
- Purpose: Data transformation and formatting according to Boyens Media specifications
- Location: `web/app.py` (formatting functions), `web/churchdesk_api.py` (event analysis and transformation)
- Contains: Service type mapping, date/time formatting, pastor name formatting, location extraction
- Depends on: Data from Excel or ChurchDesk API
- Used by: Route handlers for output generation

**API Integration Layer:**
- Purpose: ChurchDesk API client for fetching church service events from multiple organizations
- Location: `web/churchdesk_api.py`
- Contains: HTTP request handling, event pagination, organization management, event filtering by category
- Depends on: requests library, external ChurchDesk API (v3.0.0)
- Used by: Web routes for real-time event fetching

**Data Processing Layer:**
- Purpose: Excel file reading and DataFrame manipulation
- Location: `web/app.py` (process_excel_file function)
- Contains: Pandas DataFrame operations, column validation, data sorting and grouping
- Depends on: openpyxl, pandas
- Used by: Upload route handler

## Data Flow

**Excel Upload Path:**
1. User selects `.xlsx` file on index.html
2. File POSTed to `/upload` endpoint
3. Flask saves temp file
4. `process_excel_file()` reads Excel via pandas
5. Validates required columns: `Startdatum`, `Titel`, `Standortnamen`, `Mitwirkender`, `Gemeinden`
6. Groups events by date
7. Applies formatting functions to each field
8. Returns formatted text to result.html
9. User downloads as .txt or copies to clipboard

**ChurchDesk API Path:**
1. User selects organizations and month on index.html
2. Form POSTed to `/fetch_churchdesk_events`
3. `create_multi_org_client()` instantiates `MultiOrganizationChurchDeskAPI`
4. Fetches events from all selected organizations for specified month
5. `EventAnalyzer.format_event_for_boyens()` processes each event:
   - Converts UTC time to German timezone (CET/CEST)
   - Extracts location with `extract_boyens_location()`
   - Validates completeness
6. Events displayed on churchdesk_events.html
7. User selects events to export
8. `/export_selected_events` converts to Boyens format
9. Result displayed on result.html

**Output Generation (both paths):**
1. Events grouped by date
2. Date header formatted as "Weekday, Day. Month"
3. For each event:
   - Location extracted (with multi-church city logic)
   - Time formatted as "H Uhr" or "H.MM Uhr"
   - Service type mapped to Boyens abbreviations
   - Pastor formatted with prefix (P., Pn., D., etc.)
4. Line format: `Location: Time, Service Type[, Pastor Name]`
5. Blank line separates each date

**State Management:**
- No persistent state between requests
- Flask sessions used only for flash messages
- Temporary files created/deleted during processing
- ChurchDesk event data passed via JSON in HTML forms

## Key Abstractions

**ChurchDeskAPI:**
- Purpose: Single-organization API client wrapper
- Examples: `web/churchdesk_api.py` lines 43-157
- Pattern: Wrapper around requests.Session with authenticated endpoint calls

**MultiOrganizationChurchDeskAPI:**
- Purpose: Aggregates data from multiple ChurchDesk organizations
- Examples: `web/churchdesk_api.py` lines 425-511
- Pattern: Manages collection of ChurchDeskAPI clients with shared organization configuration

**EventAnalyzer:**
- Purpose: Analyzes event completeness and formats for output
- Examples: `web/churchdesk_api.py` lines 159-245
- Pattern: Static utility class with pure transformation functions

**Location Extraction (extract_boyens_location):**
- Purpose: Maps raw location names to Boyens Media format with city/church logic
- Examples: `web/churchdesk_api.py` lines 248-355
- Pattern: Configuration-driven mapping with conditional logic for multi-church cities

**Formatting Functions:**
- Purpose: Convert raw data to publication-ready German text
- Examples:
  - `format_date()` - German weekday/month names
  - `format_time()` - "H Uhr" or "H.MM Uhr" format
  - `format_service_type()` - Maps titles to abbreviations (Gd., Gd. m. A., etc.)
  - `format_pastor()` / `format_boyens_pastor()` - Prefix normalization
- Pattern: Pure functions with configurable mappings

## Entry Points

**Web Application:**
- Location: `web/app.py` lines 403-404
- Triggers: `python app.py` (development) or Flask WSGI (production)
- Responsibilities: Flask app initialization and server startup

**Index Route:**
- Location: `web/app.py` lines 171-173
- Triggers: GET `/`
- Responsibilities: Render main form with organization selection and file upload

**Upload Route:**
- Location: `web/app.py` lines 175-207
- Triggers: POST `/upload` with file
- Responsibilities: Process Excel file and return formatted result

**ChurchDesk Fetch Route:**
- Location: `web/app.py` lines 234-304
- Triggers: POST `/fetch_churchdesk_events` with year, month, organization IDs
- Responsibilities: Fetch and display filtered events for user selection

**Export Route:**
- Location: `web/app.py` lines 307-339
- Triggers: POST `/export_selected_events` with selected event IDs
- Responsibilities: Convert selected events to Boyens format and display result

**Download Route:**
- Location: `web/app.py` lines 209-231
- Triggers: POST `/download` with formatted text
- Responsibilities: Send formatted text as .txt file attachment

**Standalone Script:**
- Location: `gottesdienst_formatter_final.py`
- Triggers: Command line execution
- Responsibilities: Interactive Excel file processing for non-web use

## Error Handling

**Strategy:** Try-catch at route level with user-facing flash messages

**Patterns:**
- Excel processing: Column validation with `ValueError` exception
- API requests: `requests.exceptions.RequestException` caught as generic ChurchDesk error
- File operations: `tempfile.NamedTemporaryFile` with automatic cleanup via `delete=False` + manual `os.unlink()`
- Invalid file format: Check `file.filename.endswith('.xlsx')`
- Missing data: Flash message and redirect to index
- API failures: Graceful handling in multi-org loop with `continue` (skip failed org, process others)

## Cross-Cutting Concerns

**Logging:** No structured logging framework; relies on Python print() statements in API client for errors

**Validation:**
- Excel: Required column presence validated before processing
- File: MIME type checked (`.xlsx` extension only)
- API: Event completeness analyzed per event with `EventAnalyzer.analyze_event_completeness()`
- Data completeness: ChurchDesk events checked for required fields (title, date, location/parish, contributor)

**Authentication:**
- ChurchDesk: API tokens stored in `ORGANIZATIONS` dict in `churchdesk_api.py`
- Web app: No authentication required (public interface)
- Docker: Environment variable fallbacks for token configuration

**Timezone Handling:**
- ChurchDesk API returns UTC times with `Z` suffix
- Converted to German timezone (Europe/Berlin) using pytz
- Handles both CET and CEST (daylight saving)
- See `web/churchdesk_api.py` lines 214-218

---

*Architecture analysis: 2026-03-21*
