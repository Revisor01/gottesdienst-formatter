# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a German church service formatter tool for Boyens Medien publishing company. It converts Excel spreadsheets containing church service data into formatted text suitable for publication. The project has two main components:

1. **Standalone Python Script** (`gottesdienst_formatter_final.py`) - Command-line tool
2. **Web Application** (`web/`) - Flask-based web interface with Docker deployment

## Architecture

The application processes Excel files with church service data and formats them into German text output following specific publishing requirements. Key components:

- **Data Processing**: Excel files → Pandas DataFrame → Formatted text output
- **Web Interface**: Flask app with file upload, processing, and download functionality
- **Deployment**: Docker-based containerization with docker-compose

## Development Environment

### Python Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies for standalone script
pip install pandas openpyxl

# For web application
cd web
pip install -r requirements.txt
```

### Running the Applications

**Standalone Script:**
```bash
python gottesdienst_formatter_final.py
```

**Web Application (Development):**
```bash
cd web
python app.py
```

**Web Application (Production):**
```bash
cd web
docker compose up -d
```

## Excel Data Structure

The application expects Excel files with these columns:
- `Startdatum` - Date and time (datetime format)
- `Titel` - Service type (e.g., "Gottesdienst", "Abendmahl")
- `Standortnamen` - Church/location name
- `Mitwirkender` - Pastor/minister name
- `Gemeinden` - Parish name (fallback for location)

## Key Code Patterns

### Date/Time Formatting
- Uses German weekday/month names
- Format: "Sonnabend, 5. April" for dates
- Format: "9.30 Uhr" for times (no minutes if zero)

### Service Type Abbreviations
- `Gd.` = Standard service
- `Gd. m. A.` = Service with communion
- `Gd. m. T.` = Service with baptism
- `Konfirmation` = Confirmation
- `Familiengd.` = Family service

### Pastor Title Formatting
- Automatically converts to `P. [Name]` or `Pn. [Name]` format
- Handles various input formats (Pastor, Pastorin, etc.)

## Docker Configuration

The web application uses:
- Port 5000 (container) → 5000 (host)
- Volume mapping for uploads: `./uploads:/app/uploads`
- Production environment variables set in docker-compose.yml

## Testing

No formal test suite is currently implemented. Testing is done manually:
1. Use sample Excel files from the project
2. Verify output format matches Boyens Medien requirements
3. Check German date/time formatting
4. Validate service type abbreviations

## Deployment

### Server Information
- **Server**: 185.248.143.234
- **User**: root (not simon)
- **Application Path**: /opt/ (not /var/www/)
- **Access**: `ssh root@185.248.143.234`

### Deployment Process
The deployment uses GitHub for code distribution:

1. **Push changes to GitHub**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

2. **Deploy to server**:
   ```bash
   ssh root@185.248.143.234
   cd /opt/gottesdienst-formatter
   git pull origin main
   cd web
   docker compose build --no-cache
   docker compose up -d
   ```

### ChurchDesk API Integration
The application integrates with ChurchDesk API for multiple church organizations:
- Organization tokens are configured in `churchdesk_api.py`
- Multi-organization support for fetching church service data
- Boyens Media format compliance with intelligent location extraction

## Common Development Tasks

- **Add new service type**: Update `format_service_type()` function in both scripts
- **Modify date formatting**: Update `format_date()` function 
- **Change output format**: Modify the formatting logic in `process_excel_file()`
- **Add new Excel columns**: Update `required_columns` list and processing logic
- **Deploy changes**: Push to GitHub, then pull and rebuild on server