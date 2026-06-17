#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChurchDesk API Client
Pastor Simon Luthe - Kirchenkreis Dithmarschen
"""

import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from config import ORGANIZATIONS
from formatting import format_pastor

class ChurchDeskAPI:
    """Client for ChurchDesk API interactions"""
    
    def __init__(self, api_token: str, organization_id: int):
        self.api_token = api_token
        self.organization_id = organization_id
        self.base_url = "https://api2.churchdesk.com/api/v3.0.0"
        self.session = requests.Session()
        self._gottesdienst_category_id = None
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to ChurchDesk API"""
        if params is None:
            params = {}
        
        params.update({
            'partnerToken': self.api_token,
            'organizationId': self.organization_id
        })
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"ChurchDesk API Error: {str(e)}")
    
    def get_event_categories(self) -> List[Dict]:
        """Fetch available event categories"""
        return self._make_request("events/categories")
    
    def get_event_resources(self) -> List[Dict]:
        """Fetch available event resources"""
        return self._make_request("events/resources")
    
    def get_events(self, 
                   start_date: datetime, 
                   end_date: datetime,
                   category_ids: List[int] = None,
                   resource_ids: List[int] = None,
                   items_per_page: int = 100) -> List[Dict]:
        """
        Fetch events for specified date range
        
        Args:
            start_date: Start date for events
            end_date: End date for events
            category_ids: List of category IDs to filter by
            resource_ids: List of resource IDs to filter by
            items_per_page: Number of items per page (max 100)
        """
        params = {
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'itemsNumber': min(items_per_page, 100)
        }
        
        if category_ids:
            params['cid'] = category_ids
        
        if resource_ids:
            params['rid'] = resource_ids
        
        return self._make_request("events", params)
    
    def get_gottesdienst_category_id(self) -> Optional[int]:
        """Get the Gottesdienst category ID for this organization"""
        if self._gottesdienst_category_id is not None:
            return self._gottesdienst_category_id
        
        categories = self.get_event_categories()
        for category in categories:
            if 'gottesdienst' in category['name'].lower():
                self._gottesdienst_category_id = category['id']
                return self._gottesdienst_category_id
        
        return None
    
    def get_gottesdienst_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch only 'Gottesdienst' (church service) events
        
        Args:
            start_date: Start date for events
            end_date: End date for events
        """
        gottesdienst_category_id = self.get_gottesdienst_category_id()
        
        if gottesdienst_category_id:
            return self.get_events(start_date, end_date, category_ids=[gottesdienst_category_id])
        else:
            # If no specific Gottesdienst category found, get all events
            return self.get_events(start_date, end_date)
    
    def get_monthly_events(self, year: int, month: int) -> List[Dict]:
        """
        Fetch events for a specific month
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
        """
        # First day of month
        start_date = datetime(year, month, 1)
        
        # Last day of month
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return self.get_gottesdienst_events(start_date, end_date)


class EventAnalyzer:
    """Analyze ChurchDesk events for completeness and formatting"""
    
    @staticmethod
    def analyze_event_completeness(event: Dict) -> Dict:
        """
        Analyze an event for missing required data
        
        Returns:
            Dict with missing_fields list and completeness score
        """
        required_fields = {
            'title': event.get('title'),
            'startDate': event.get('startDate'),
            'location': event.get('location') or event.get('locationName'),
            'contributor': event.get('contributor'),
            'parishes': event.get('parishes', [])
        }
        
        # German translations for field names
        field_translations = {
            'title': 'Titel',
            'startDate': 'Startdatum',
            'location': 'Ort',
            'contributor': 'Mitwirkender',
            'parishes': 'Gemeinde'
        }
        
        missing_fields = []
        
        for field, value in required_fields.items():
            if not value:
                missing_fields.append(field_translations[field])
            elif field == 'parishes' and len(value) == 0:
                missing_fields.append(field_translations[field])
        
        completeness_score = (len(required_fields) - len(missing_fields)) / len(required_fields)
        
        return {
            'missing_fields': missing_fields,
            'completeness_score': completeness_score,
            'is_complete': len(missing_fields) == 0
        }
    
    @staticmethod
    def format_event_for_boyens(event: Dict) -> Optional[Dict]:
        """
        Format ChurchDesk event for Boyens Media output
        
        Returns:
            Dict with formatted event data or None if essential data missing
        """
        analysis = EventAnalyzer.analyze_event_completeness(event)
        
        if 'startDate' not in analysis['missing_fields']:
            # Parse UTC time and convert to German time (CET/CEST)
            utc_time = datetime.fromisoformat(event['startDate'].replace('Z', '+00:00'))
            utc_time = utc_time.replace(tzinfo=pytz.UTC)
            german_tz = pytz.timezone('Europe/Berlin')
            start_date = utc_time.astimezone(german_tz)
            
            # Extract location - prefer locationName over location
            location = event.get('locationName') or event.get('location', '')
            
            # Get parish name as fallback
            parish_name = ''
            if event.get('parishes'):
                parish_name = event['parishes'][0].get('title', '')
            
            # Use location or parish as fallback
            raw_location = location or parish_name
            
            # Apply location mapping for display (keep Urlauberseelsorge as is)
            final_location = extract_boyens_location(raw_location, for_export=False)
            
            return {
                'id': event['id'],
                'title': event.get('title', 'Gottesdienst'),
                'startDate': start_date,
                'location': final_location,
                'contributor': event.get('contributor', ''),
                'parishes': event.get('parishes', []),
                'original_event': event,
                'analysis': analysis
            }
        
        return None


# Orte mit MEHREREN Kirchen — hier muss der konkrete Kirchenname genannt werden
# statt nur "Ort, Kirche". EXAKTER Ortsvergleich (kein Substring), damit
# "Heide-Süderholm" o.ae. nicht faelschlich als Multi-Kirchen-Ort gelten.
MULTI_CHURCH_CITIES = ['heide', 'brunsbüttel', 'büsum', 'burg', 'marne']

# Wortbestandteile, die eine Location als Kirche kennzeichnen.
_CHURCH_WORDS = ('kirche', 'dom', 'kapelle', 'münster', 'muenster')

# Stichwoerter, die eine separatorlose Location als NICHT-Kirche kennzeichnen
# (weltliche Orte). Solche Eintraege bleiben unveraendert (kein ", Kirche").
_NON_CHURCH_WORDS = (
    'badestelle', 'bootshafen', 'fähranleger', 'faehranleger', 'schwimmbad',
    'sportplatz', 'reitplatz', 'grundschule', 'schule', 'schulhof', 'mühle',
    'muehle', 'hof ', 'schutzhütte', 'schutzhuette', 'forst', 'wald', 'halle',
    'gemeindehaus', 'gemeindesaal', 'saal', 'dörpshus', 'doerpshus', 'haus ',
    'gänsemarkt', 'gaensemarkt', 'markt', 'steinzeitpark', 'park', 'papenbusch',
    'familie ', 'altenhilfezentrum', 'gemeindezentrum', 'pastorat', 'küche',
    'kueche', 'blockhütte', 'blockhuette', 'feuerwehr', 'mühlenteich', 'ankerplatz',
)

# Exakte Kirchen-/Ortsmappings (nach Normalisierung exakt, NICHT als Substring,
# sonst matcht z.B. "st. andreas-kirche" auch in "St. Andreas-Kirche Büsum").
# Nur fuer Einzelkirchen-Orte: liefern den Boyens-Ortsnamen.
_LOCATION_MAPPINGS = {
    'st. annen-kirche': 'St. Annen',
    'st. marien-kirche': 'Eddelak',
    'marien-kirche': 'Eddelak',
    'st. laurentius-kirche': 'Lunden',
    'st. rochus-kirche': 'Schlichting',
    'st. andreas-kirche': 'Weddingstedt',
    'st. secundus-kirche': 'Hennstedt',
    'st. bartholomäus': 'Wesselburen',
    'kreuzkirche wesseln': 'Wesseln',
    'kirche wesseln': 'Wesseln',
    # Tellingstedt — St. Martins-Kirche (diverse Schreibweisen aus ChurchDesk)
    'st. martins-kirche': 'Tellingstedt',
    'st. martinskirche': 'Tellingstedt',
    'st. martins-kirche tellingstedt': 'Tellingstedt',
    'st. martinskirche tellingstedt': 'Tellingstedt',
    'tellingstedt st. martinskirche': 'Tellingstedt',
    'tellingstedt st. marinskirche': 'Tellingstedt',
    # Albersdorf — St. Remigius-Kirche
    'st. remigius-kirche': 'Albersdorf',
    'st. remigius kirche': 'Albersdorf',
    'st. remigius-kirche albersdorf': 'Albersdorf',
    'st. remigius kirche albersdorf': 'Albersdorf',
}


def _has_church_word(text: str) -> bool:
    """True, wenn der Text eine Kirche bezeichnet.

    Erkennt explizite Kirchen-Woerter (Kirche/Dom/Kapelle/Münster) sowie
    Heiligen-Patrozinien ohne das Wort 'Kirche' (z.B. "St. Jacobi",
    "St. Bartholomäus") — typische Einzelkirchen-Namen.
    """
    t = text.strip().lower()
    if any(w in t for w in _CHURCH_WORDS):
        return True
    # Patrozinium: "St. <Name>" / "St.<Name>" als Kirchenname
    if t.startswith('st. ') or t.startswith('st.') or t.startswith('sankt '):
        return True
    return False


def _strip_church_suffix(name: str) -> str:
    """Entfernt ein abschliessendes ' Kirche' (mit Space) — fuer 'Hennstedt Kirche'."""
    for suf in (' Kirche', ' kirche'):
        if name.endswith(suf):
            return name[:-len(suf)].strip()
    return name


def _is_standalone_name(text: str) -> bool:
    """True, wenn der Text als Eigenname stehen bleibt und KEIN ", Kirche" bekommt.

    Trifft auf eigenstaendige Kirchennamen (Dom/Kirche/Patrozinium) und auf
    weltliche Orte (Badestelle, Sportplatz, Hof, ...) zu.
    """
    t = text.lower()
    # Nur ECHTE Kirchen-Woerter (NICHT das "St."-Patrozinium-Praefix) — sonst
    # wuerde der Ortsname "St. Annen" faelschlich als Kirche gelten und kein
    # ", Kirche" bekommen.
    if any(w in t for w in _CHURCH_WORDS):
        return True
    if any(w in t for w in _NON_CHURCH_WORDS):
        return True
    return False


def extract_boyens_location(location_name: str, location_obj: Dict = None, for_export: bool = True) -> str:
    """
    Boyens-Ortsausgabe.

    Ermittelt den normalisierten Ort/Kirchennamen (_resolve_location). Beim Export
    wird je Einzel-Kirchen-Ort ", Kirche" ergaenzt; Multi-Kirchen-Orte
    (Heide/Brunsbuettel/Buesum/Burg/Marne) nennen ihren konkreten Kirchennamen,
    Nicht-Kirchen-Orte (Gemeindehaus, Saal, ...) schreiben die Location aus.
    """
    resolved = _resolve_location(location_name, location_obj, for_export)

    if not for_export or not resolved:
        return resolved

    # Bereits eine zusammengesetzte Bezeichnung mit Komma (Kirchenname oder
    # ausgeschriebene Location) → unveraendert lassen.
    if ',' in resolved:
        return resolved
    # Multi-Kirchen-Ort OHNE konkrete Kirche (z.B. "Büsum" via St. Clemens):
    # kein generisches ", Kirche". Exakter Vergleich (Substring-Bug-Schutz).
    if resolved.lower() in MULTI_CHURCH_CITIES:
        return resolved
    # Eigenstaendiger Kirchenname (z.B. "Meldorfer Dom", "St. Martins-Kirche")
    # oder weltlicher Ort (Badestelle, Sportplatz, ...) → unveraendert lassen,
    # KEIN doppeltes / falsches ", Kirche".
    if _is_standalone_name(resolved):
        return resolved
    # Reiner Ortsname → Dorfkirche-Annahme: "Ort, Kirche"
    return "{}, Kirche".format(resolved)


def _resolve_location(location_name: str, location_obj: Dict = None, for_export: bool = True) -> str:
    """Normalisiert eine rohe ChurchDesk-Location zu Ort bzw. Ort+Kirche/Location.

    Gibt den reinen Ortsnamen zurueck (ohne ", Kirche"-Suffix — das ergaenzt der
    Wrapper), oder bei Multi-Kirchen/Nicht-Kirchen eine "Ort, X"-Bezeichnung.
    """
    if not location_name:
        return ""

    location = location_name.strip()
    if not location:
        return ""

    # 1) Separatoren vereinheitlichen: "Ort | X" / "Ort - X" → (Ort, X)
    city, rest = location, None
    for sep in (' | ', ' - '):
        if sep in location:
            city, rest = location.split(sep, 1)
            city, rest = city.strip(), rest.strip()
            break
    else:
        # Komma-Separator: "Ort, X"
        if ', ' in location:
            city, rest = location.split(', ', 1)
            city, rest = city.strip(), rest.strip()
        else:
            # Space-Separator NUR fuer Multi-Kirchen-Orte: "Heide St.-Jürgen-Kirche".
            # Nicht bei Bindestrich-Kompositum ("Heide-Süderholm" bleibt ganz).
            loc_lower = location.lower()
            for mc in MULTI_CHURCH_CITIES:
                if loc_lower.startswith(mc + ' ') and not loc_lower.startswith(mc + '-'):
                    city = location[:len(mc)]
                    rest = location[len(mc) + 1:].strip()
                    break

    city_lower = city.lower()

    # 2) Exakte Mappings auf der GESAMT-Location (z.B. "St. Secundus-Kirche")
    mapped = _LOCATION_MAPPINGS.get(location.lower())
    if mapped:
        return mapped
    # Urlauberseelsorge — Anzeige behaelt den Begriff, Export → Büsum
    if location.lower() in ('urlauberseelsorge', 'urlauberseelsorge büsum'):
        return 'Büsum' if for_export else 'Urlauberseelsorge'

    # 3) Multi-Kirchen-Orte: konkreten Kirchennamen nennen
    if city_lower in MULTI_CHURCH_CITIES:
        # Büsum-Sonderfaelle
        if city_lower == 'büsum':
            if rest and 'st. clemens' in rest.lower():
                return 'Büsum'                       # Hauptkirche → nur Büsum
            if rest and 'perlebucht' in rest.lower():
                return 'Büsum, Perlebucht'
            if rest and _has_church_word(rest):
                return 'Büsum, {}'.format(rest)
            if rest:
                return 'Büsum, {}'.format(rest)      # Nicht-Kirche ausschreiben
            return 'Büsum'
        # Heide/Brunsbüttel/Burg/Marne
        if rest:
            return '{}, {}'.format(city, rest)       # Kirchenname/Location nennen
        return city

    # 4) Einzelkirchen-Ort
    if rest is not None:
        # Rest ist eine Kirche → "Ort, Kirche"; sonst Location ausschreiben
        if _has_church_word(rest):
            return '{}, Kirche'.format(city)
        return '{}, {}'.format(city, rest)

    # 5) Kein Separator.
    # 5a) "Ort Kirche" (Space-Suffix) → reiner Ort, Wrapper macht "Ort, Kirche".
    stripped = _strip_church_suffix(location)
    if stripped != location:
        return stripped                  # "Hennstedt Kirche" → "Hennstedt"

    # 5b/5c) Eigenstaendiger Kirchenname (z.B. "Meldorfer Dom") oder weltlicher
    # Ort (Badestelle, Sportplatz, ...) → unveraendert. Der Wrapper erkennt das
    # ebenfalls ueber _is_standalone_name() und haengt KEIN ", Kirche" an.
    return location


class MultiOrganizationChurchDeskAPI:
    """Client for managing multiple ChurchDesk organizations"""
    
    def __init__(self, selected_org_ids: List[int] = None):
        """
        Initialize multi-organization API client
        
        Args:
            selected_org_ids: List of organization IDs to include. If None, include all available.
        """
        if selected_org_ids is None:
            selected_org_ids = list(ORGANIZATIONS.keys())
        
        self.clients = {}
        self.org_info = {}
        
        for org_id in selected_org_ids:
            if org_id in ORGANIZATIONS:
                config = ORGANIZATIONS[org_id]
                self.clients[org_id] = ChurchDeskAPI(config['token'], org_id)
                self.org_info[org_id] = {
                    'name': config['name'],
                    'description': config['description']
                }
    
    def get_available_organizations(self) -> Dict[int, Dict]:
        """Get information about available organizations"""
        return {org_id: ORGANIZATIONS[org_id] for org_id in ORGANIZATIONS.keys()}
    
    def get_selected_organizations(self) -> Dict[int, Dict]:
        """Get information about selected organizations"""
        return self.org_info
    
    def get_all_events(self, start_date: datetime, end_date: datetime, 
                       gottesdienst_only: bool = True) -> List[Dict]:
        """
        Fetch events from all selected organizations
        
        Args:
            start_date: Start date for events
            end_date: End date for events
            gottesdienst_only: If True, fetch only Gottesdienst events
        
        Returns:
            List of events with organization info added
        """
        all_events = []
        
        for org_id, client in self.clients.items():
            try:
                if gottesdienst_only:
                    events = client.get_gottesdienst_events(start_date, end_date)
                else:
                    events = client.get_events(start_date, end_date)
                
                # Add organization info to each event
                for event in events:
                    event['organization_id'] = org_id
                    event['organization_name'] = self.org_info[org_id]['name']
                    all_events.append(event)
                    
            except Exception as e:
                print(f"Error fetching events from org {org_id}: {e}")
                continue
        
        # Sort all events by date
        all_events.sort(key=lambda x: x['startDate'])
        return all_events
    
    def get_monthly_events(self, year: int, month: int, 
                          gottesdienst_only: bool = True) -> List[Dict]:
        """
        Fetch events for a specific month from all organizations
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            gottesdienst_only: If True, fetch only Gottesdienst events
        """
        # Calculate start and end dates
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return self.get_all_events(start_date, end_date, gottesdienst_only)


def create_api_client() -> ChurchDeskAPI:
    """Create ChurchDesk API client from environment variables (backwards compatibility)"""
    api_token = os.getenv('CHURCHDESK_API_TOKEN')
    organization_id = os.getenv('CHURCHDESK_ORGANIZATION_ID')
    
    if not api_token:
        api_token = ORGANIZATIONS.get(2596, {}).get('token')
    
    if not organization_id:
        organization_id = "2596"  # Default to Kirchenkreis
    
    try:
        org_id = int(organization_id)
    except ValueError:
        raise ValueError("CHURCHDESK_ORGANIZATION_ID must be a valid integer")
    
    if org_id in ORGANIZATIONS:
        config = ORGANIZATIONS[org_id]
        return ChurchDeskAPI(config['token'], org_id)
    else:
        if not api_token:
            raise ValueError("No API token available for the specified organization")
        return ChurchDeskAPI(api_token, org_id)


def create_multi_org_client(selected_org_ids: List[int] = None) -> MultiOrganizationChurchDeskAPI:
    """Create multi-organization ChurchDesk API client"""
    return MultiOrganizationChurchDeskAPI(selected_org_ids)