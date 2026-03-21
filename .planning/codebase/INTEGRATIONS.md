# External Integrations

**Analysis Date:** 2026-03-21

## APIs & External Services

**ChurchDesk API:**
- Service: Church management and event scheduling system (https://api2.churchdesk.com/api/v3.0.0)
- What it's used for: Fetching church service events (Gottesdienste) for multiple organizations
  - SDK/Client: `requests` library + custom `ChurchDeskAPI` class in `web/churchdesk_api.py`
  - Auth: Bearer token via `partnerToken` query parameter
  - Multi-org support: 5 configured organizations in `ORGANIZATIONS` dict

**ChurchDesk Organizations:**
The application integrates with 5 church organizations:
1. **Kirchenkreis Dithmarschen** (ID: 2596)
   - Token: d4ec66780546786c92b916f873ee713181c1b695d32e7ba9839e760eaecd3fa1
   - Purpose: Central district administration

2. **Kirchspiel Heide** (ID: 6572)
   - Token: 7b0cf910b378c6d2482419f4e785fc95b18c1ec6fbfdd6dea48085b58f52e894
   - Parishes: Heide (St.-Jürgen, Erlöser, Auferstehung), Nordhastedt, Wesseln, Hemmingstedt, Eddelak

3. **KG Hennstedt (alt)** (ID: 2719)
   - Token: c2d76c9414f6aac773c1643a98131123dbfc2ae7c31e4d2e864974c131dccedf
   - Purpose: Hennstedt main church only (legacy)

4. **Kirchspiel Eider** (ID: 2725)
   - Token: 3afe57b4ae54ece02ff568993777028b47995601ecab92097e30a66f4d90494d
   - Parishes: Hennstedt, Lunden, Hemme, St. Annen, Schlichting, Weddingstedt, Ostrohe, Stelle-Wittenwurth

5. **Kirchspiel West** (ID: 2729)
   - Token: bZq4GLCvhUbkYFQrDVDAe3cTs8hVlyQqEUmQ6xW5Tjw2EMEm3lCgYI6LSj3lrhvf7MTDIHL3TdrVXYdV
   - Parishes: Büsum, Neuenkirchen, Wesselburen, Urlauberseelsorge

## Data Processing

**Excel Files:**
- Format: .xlsx (Office Open XML)
- Location: User uploads or command-line source
- Parsing: openpyxl library via pandas
- Required columns: `Startdatum`, `Titel`, `Standortnamen`, `Mitwirkender`, `Gemeinden`
- Export: Text file output in Boyens Media format

**Output Format:**
- Text files (.txt) with UTF-8 encoding
- Location: `web/uploads/` directory (persistent volume in Docker)
- Format: German date/time with church service details for publication

## Data Storage

**Databases:**
- None detected - Stateless application

**File Storage:**
- Local filesystem only
- Upload directory: `./uploads/` mapped via docker-compose volume
- Temporary files: System temp directory (`tempfile.NamedTemporaryFile`)

**Caching:**
- None detected - All requests are fresh

## Authentication & Identity

**ChurchDesk API Authentication:**
- Method: Token-based query parameter authentication
- Implementation: `partnerToken` query parameter in all API requests (`web/churchdesk_api.py` line 59)
- Location: Embedded in ORGANIZATIONS dict (hardcoded tokens for known orgs)
- Environment override: `CHURCHDESK_API_TOKEN` env var can override defaults

**Flask Application Security:**
- Secret key: `gottesdienst-formatter-secret-key` (hardcoded in `web/app.py` line 19)
- Session management: Flask default session handling

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logging:**
- Standard output/console logging only
- Flask debug mode disabled in production
- Error messages captured in try-catch blocks and displayed via Flask `flash()`

## CI/CD & Deployment

**Hosting:**
- Hetzner server (185.248.143.234)
- Docker containerization
- Application path: `/opt/gottesdienst-formatter/`

**CI Pipeline:**
- Not detected - Manual deployment via Git

**Deployment Process:**
- GitHub repository for version control
- Manual ssh + git pull → docker compose rebuild
- One-line deployment command provided in CLAUDE.md

## Environment Configuration

**Required env vars:**
- `CHURCHDESK_API_TOKEN` - ChurchDesk API authentication (optional - defaults to org 2596 token)
- `CHURCHDESK_ORGANIZATION_ID` - Organization to fetch from (optional - defaults to 2596)
- `FLASK_ENV` - Flask environment mode (production/development)
- `FLASK_DEBUG` - Debug mode flag (false in production)

**Secrets location:**
- docker-compose.yml for environment variable defaults
- .env file or docker-compose environment section (see `.env.example`)
- Hardcoded fallback tokens in `web/churchdesk_api.py` ORGANIZATIONS dict

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected - Application reads only from ChurchDesk API

## API Endpoints Used from ChurchDesk

**GET /events/categories**
- Purpose: Fetch available event category types
- Used in: `ChurchDeskAPI.get_event_categories()` → identifies "Gottesdienst" category

**GET /events/resources**
- Purpose: Fetch available resources/locations
- Used in: `ChurchDeskAPI.get_event_resources()`

**GET /events**
- Purpose: Fetch events for date range with optional filtering
- Parameters: `startDate`, `endDate`, `cid` (category IDs), `rid` (resource IDs)
- Used in: Monthly event fetching with Gottesdienst category filtering

## Multi-Organization Workflow

**Data Flow:**
1. User selects organizations via web form
2. `create_multi_org_client(selected_org_ids)` creates `MultiOrganizationChurchDeskAPI` instance
3. Each organization gets dedicated `ChurchDeskAPI` client with its token
4. `get_monthly_events()` fetches from all orgs in parallel
5. Events tagged with `organization_id` and `organization_name`
6. User selects events for export
7. `EventAnalyzer.format_event_for_boyens()` applies location/pastor formatting
8. Text output in Boyens Media format with church service details

---

*Integration audit: 2026-03-21*
