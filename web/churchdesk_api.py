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

# Configuration for all available organizations
ORGANIZATIONS = {
    2596: {
        'name': 'Kirchenkreis Dithmarschen',
        'token': 'd4ec66780546786c92b916f873ee713181c1b695d32e7ba9839e760eaecd3fa1',
        'description': 'Zentrale Verwaltung'
    },
    6572: {
        'name': 'Kirchspiel Heide',
        'token': '7b0cf910b378c6d2482419f4e785fc95b18c1ec6fbfdd6dea48085b58f52e894',
        'description': 'Heide (St.-Jürgen, Erlöser, Auferstehung), Nordhastedt, Wesseln, Hemmingstedt, Eddelak'
    },
    2719: {
        'name': 'KG Hennstedt (alt)',
        'token': 'c2d76c9414f6aac773c1643a98131123dbfc2ae7c31e4d2e864974c131dccedf',
        'description': 'Nur Hennstedt Hauptkirche'
    },
    2725: {
        'name': 'Kirchspiel Eider',
        'token': '3afe57b4ae54ece02ff568993777028b47995601ecab92097e30a66f4d90494d',
        'description': 'Hennstedt, Lunden, Hemme, St. Annen, Schlichting, Weddingstedt, Ostrohe, Stelle-Wittenwurth'
    },
    2729: {
        'name': 'Kirchspiel West',
        'token': 'bZq4GLCvhUbkYFQrDVDAe3cTs8hVlyQqEUmQ6xW5Tjw2EMEm3lCgYI6LSj3lrhvf7MTDIHL3TdrVXYdV',
        'description': 'Büsum, Neuenkirchen, Wesselburen, Urlauberseelsorge'
    }
}

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
            final_location = location or parish_name
            
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


def extract_boyens_location(location_name: str, location_obj: Dict = None) -> str:
    """
    Extract location name according to Boyens Media format rules:
    - Single church per city: just city name
    - Multiple churches per city: "City, Church Name"
    - Special handling for known multi-church cities
    """
    if not location_name:
        return ""
    
    # Multi-church cities that need church specification
    MULTI_CHURCH_CITIES = ['heide', 'brunsbüttel', 'büsum']
    
    # Clean and normalize location name
    location = location_name.strip()
    
    # Handle pipe separator format: "City | Church"
    if ' | ' in location:
        parts = location.split(' | ')
        city = parts[0].strip()
        church = parts[1].strip()
        
        # Check if city has multiple churches
        city_lower = city.lower()
        if any(multi_city in city_lower for multi_city in MULTI_CHURCH_CITIES):
            # Special case for standard church names
            if 'st. clemens' in church.lower():
                return city  # "Büsum" instead of "Büsum, St. Clemens-Kirche"
            elif 'gemeindehaus' in church.lower() or 'kapelle' in church.lower():
                return f"{city}, {church}"
            else:
                return f"{city}, {church}"
        else:
            return city  # Single church cities: just city name
    
    # Handle comma separator format: "City, Church"
    if ', ' in location:
        parts = location.split(', ', 1)
        city = parts[0].strip()
        church = parts[1].strip()
        
        city_lower = city.lower()
        if any(multi_city in city_lower for multi_city in MULTI_CHURCH_CITIES):
            # For Heide, always show church name
            if city_lower == 'heide':
                return location  # Keep "Heide, St.-Jürgen-Kirche"
            # For other multi-church cities, check church type
            elif 'gemeindehaus' in church.lower() or 'kapelle' in church.lower():
                return location
            else:
                return city  # Standard churches: just city
        else:
            return city  # Single church cities: just city name
    
    # No separator found - likely just city name or direct church name
    location_lower = location.lower()
    
    # Special mappings
    LOCATION_MAPPINGS = {
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
        'urlauberseelsorge büsum': 'Urlauberseelsorge'
    }
    
    for church_pattern, boyens_name in LOCATION_MAPPINGS.items():
        if church_pattern in location_lower:
            return boyens_name
    
    return location


def format_boyens_pastor(contributor: str) -> str:
    """
    Format pastor name according to Boyens Media standards:
    - Diakonin/Diakon → D.
    - Pastorin → Pn.
    - Pastor → P.
    - Multiple pastors: combine with &
    - Special cases: Kirchspiel-Pastor:innen, Konfirmand:innen etc.
    """
    if not contributor:
        return ""
    
    name = str(contributor).strip()
    
    # Handle multiple contributors separated by various delimiters
    delimiters = [', ', ' & ', ' und ', ' + ', ' / ']
    contributors = [name]
    
    for delimiter in delimiters:
        if delimiter in name:
            contributors = [c.strip() for c in name.split(delimiter)]
            break
    
    formatted_contributors = []
    
    for contrib in contributors:
        # Handle special cases for individual contributors
        contrib_lower = contrib.lower()
        if 'kirchspiel-pastor:innen' in contrib_lower:
            formatted_contributors.append('Kirchspiel-Pastor:innen')
            continue
        if 'konfirmand:innen' in contrib_lower:
            formatted_contributors.append('Konfirmand:innen')
            continue
        
        # Remove existing prefixes
        prefixes = ['Pastores ', 'Pastor ', 'Pastorin ', 'Pfarrer ', 'P. ', 'Pn. ', 'Ps. ', 'Diakon ', 'Diakonin ', 'D. ', 'Dn. ', 'Prädikant ', 'Prädikantin ']
        clean_name = contrib
        for prefix in prefixes:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):].strip()
                break
        
        # Determine new prefix based on original text - be more specific in detection
        if 'diakonin' in contrib_lower:
            formatted_contributors.append(f"Dn. {clean_name}")
        elif 'diakon' in contrib_lower:
            formatted_contributors.append(f"D. {clean_name}")
        elif 'pastores' in contrib_lower:
            formatted_contributors.append(f"Ps. {clean_name}")
        elif 'pastorin' in contrib_lower:
            formatted_contributors.append(f"Pn. {clean_name}")
        elif 'pastor' in contrib_lower or 'pfarrer' in contrib_lower:
            formatted_contributors.append(f"P. {clean_name}")
        elif 'pn.' in contrib_lower:
            formatted_contributors.append(f"Pn. {clean_name}")
        elif 'p.' in contrib_lower:
            formatted_contributors.append(f"P. {clean_name}")
        elif 'prädikant' in contrib_lower:
            formatted_contributors.append(f"Prädikant {clean_name}")
        else:
            # Keep original if unclear - don't assume Pastor
            formatted_contributors.append(clean_name)
    
    return ' & '.join(formatted_contributors)


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
        # Try to use default token for org 2596
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