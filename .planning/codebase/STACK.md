# Technology Stack

**Analysis Date:** 2026-03-21

## Languages

**Primary:**
- Python 3.11 - Core application language for both standalone script and web server

**Markup/Templates:**
- Jinja2 - HTML templating within Flask application
- HTML5 - Web interface markup

## Runtime

**Environment:**
- Python 3.11-slim Docker image (`python:3.11-slim`)

**Package Manager:**
- pip - Python package management
- Lockfile: requirements.txt present

## Frameworks

**Core:**
- Flask 2.3.3 - Web application framework for `web/app.py`

**Data Processing:**
- pandas 2.3.1 - Excel parsing and data manipulation
- openpyxl 3.1.5 - Excel file I/O handling

**Web Server:**
- Werkzeug 2.3.7 - WSGI utility library (Flask dependency)

**Testing:**
- Not detected - Manual testing only per CLAUDE.md

**Build/Dev:**
- Docker - Containerization via `web/Dockerfile` and docker-compose.yml
- docker-compose 3.8 - Multi-container orchestration

## Key Dependencies

**Critical:**
- pandas 2.3.1 - Core dependency for Excel data processing and transformations
- Flask 2.3.3 - Web framework serving the user interface at port 5000 (mapped to 5001 in production)
- openpyxl 3.1.5 - Required for reading .xlsx Excel files

**Infrastructure:**
- requests 2.31.0 - HTTP client for ChurchDesk API communication
- pytz 2023.3 - Timezone handling for UTC to German time conversion (Europe/Berlin)
- Werkzeug 2.3.7 - WSGI utilities for Flask

## Configuration

**Environment:**
- FLASK_ENV - Controls Flask mode (development/production)
- FLASK_DEBUG - Disables debug mode in production
- CHURCHDESK_API_TOKEN - API token for ChurchDesk authentication
- CHURCHDESK_ORGANIZATION_ID - Organization identifier for API calls (default: 2596)

**Build:**
- `web/Dockerfile` - Container image definition with non-root user (appuser:1000)
- `web/docker-compose.yml` - Orchestration config with volume mapping for uploads
- `web/requirements.txt` - Pinned Python dependencies

## Platform Requirements

**Development:**
- Python 3.11+ (virtual environment in `venv/`)
- pip for dependency management
- Excel files in .xlsx format
- ChurchDesk API access (requires valid token)

**Production:**
- Docker and docker-compose
- Server: 185.248.143.234 (see CLAUDE.md)
- Application path: `/opt/gottesdienst-formatter`
- Port: 5000 (container) → 5001 (host via docker-compose mapping)
- URL: http://gd.kkd-fahrtenbuch.de

**Deployment:**
- Git version control for distribution
- GitHub repository for code management
- SSH access to production server for deployment

---

*Stack analysis: 2026-03-21*
