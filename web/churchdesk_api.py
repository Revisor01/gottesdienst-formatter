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


def extract_boyens_location(location_name: str, location_obj: Dict = None, for_export: bool = True) -> str:
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
            # Special case for Büsum churches
            if city_lower == 'büsum':
                if 'st. clemens' in church.lower():
                    return "Büsum"  # St. Clemens is main church = just Büsum
                elif 'perlebucht' in church.lower():
                    return "Büsum, Perlebucht"  # Keep Perlebucht specification
                else:
                    return f"Büsum, {church}"
            # Special case for Heide: remove -Kirche suffix (D-27)
            elif city_lower == 'heide':
                if church.endswith('-Kirche') or church.endswith('-kirche'):
                    church = church[:-len('-Kirche')]
                return f"{city}, {church}"
            # Special case for Brunsbüttel: keep church name (D-27)
            elif city_lower == 'brunsbüttel':
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
            # For Heide: show church name but remove -Kirche suffix (D-27)
            if city_lower == 'heide':
                if church.endswith('-Kirche') or church.endswith('-kirche'):
                    church = church[:-len('-Kirche')]
                return f"{city}, {church}"
            # For Büsum, handle special cases (D-28)
            elif city_lower == 'büsum':
                if 'st. clemens' in church.lower():
                    return "Büsum"  # St. Clemens is main church = just Büsum
                elif 'perlebucht' in church.lower():
                    return "Büsum, Perlebucht"  # Keep Perlebucht specification
                else:
                    return f"Büsum, {church}"
            # For Brunsbüttel: keep church name (D-27)
            elif city_lower == 'brunsbüttel':
                return location  # Keep "Brunsbüttel, Jakobuskirche"
            else:
                return city  # Standard single-church cities: just city
        else:
            return city  # Single church cities: just city name
    
    # Handle dash separator: "Büsum - St. Clemens-Kirche", "Büsum - Perlebucht"
    if ' - ' in location:
        parts = location.split(' - ', 1)
        city = parts[0].strip()
        church = parts[1].strip()
        # Strip -Kirche / -kirche suffix from church
        if church.endswith('-Kirche') or church.endswith('-kirche'):
            church = church[:-len('-Kirche')]
        city_lower = city.lower()
        if city_lower == 'büsum':
            if 'st. clemens' in church.lower():
                return "Büsum"  # St. Clemens ist Hauptkirche = nur Büsum
            elif 'perlebucht' in church.lower():
                return "Büsum, Perlebucht"
            else:
                return "Büsum, {}".format(church)
        elif any(mc in city_lower for mc in MULTI_CHURCH_CITIES):
            return "{}, {}".format(city, church)
        else:
            return city

    # No separator found - likely just city name or direct church name
    location_lower = location.lower()

    # Handle "Ort Kirche" without separator — detect multi-church cities first
    # Heide-Süderholm (hyphen): must NOT be split — eigener Ort
    # Heide + church: "Heide St.-Jürgen-Kirche", "Heide Erlöserkirche"
    for multi_city in MULTI_CHURCH_CITIES:
        # Match "City Church..." where City is a multi-church city
        # But NOT "City-Something" (hyphenated compounds like Heide-Süderholm)
        if location_lower.startswith(multi_city + ' ') and not location_lower.startswith(multi_city + '-'):
            city_cap = location[:len(multi_city)]  # preserve original casing
            church = location[len(multi_city) + 1:].strip()
            # Strip -Kirche / -kirche suffix
            if church.endswith('-Kirche') or church.endswith('-kirche'):
                church = church[:-len('-Kirche')]
            if church.endswith(' Kirche') or church.endswith(' kirche'):
                church = church[:-len(' Kirche')]
            city_lower_val = city_cap.lower()
            if city_lower_val == 'büsum':
                if 'st. clemens' in church.lower():
                    return "Büsum"
                elif 'perlebucht' in church.lower():
                    return "Büsum, Perlebucht"
                else:
                    return "Büsum, {}".format(church)
            else:
                return "{}, {}".format(city_cap, church)

    # Single-church towns: strip trailing " Kirche" / " kirche"
    if location.endswith(' Kirche') or location.endswith(' kirche'):
        return location[:-len(' Kirche')].strip()

    # Special mappings - different for display vs export
    if for_export:
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
            'urlauberseelsorge büsum': 'Büsum',
            'urlauberseelsorge': 'Büsum'
        }
    else:
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
            'urlauberseelsorge büsum': 'Urlauberseelsorge',
            'urlauberseelsorge': 'Urlauberseelsorge'
        }
    
    for church_pattern, boyens_name in LOCATION_MAPPINGS.items():
        if church_pattern in location_lower:
            return boyens_name
    
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