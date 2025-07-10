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

# Configuration for all available organizations
ORGANIZATIONS = {
    2596: {
        'name': 'Kirchenkreis Dithmarschen',
        'token': 'd4ec66780546786c92b916f873ee713181c1b695d32e7ba9839e760eaecd3fa1',
        'description': 'Zentrale Verwaltung'
    },
    6572: {
        'name': 'KG Heide',
        'token': '7b0cf910b378c6d2482419f4e785fc95b18c1ec6fbfdd6dea48085b58f52e894',
        'description': 'St.-Jürgen-Kirche & Auferstehungskirche'
    },
    2719: {
        'name': 'KG Hennstedt',
        'token': 'c2d76c9414f6aac773c1643a98131123dbfc2ae7c31e4d2e864974c131dccedf',
        'description': 'St. Secundus-Kirche'
    },
    2729: {
        'name': 'KG Büsum, Wesselburen, Neuenkirchen',
        'token': 'bZq4GLCvhUbkYFQrDVDAe3cTs8hVlyQqEUmQ6xW5Tjw2EMEm3lCgYI6LSj3lrhvf7MTDIHL3TdrVXYdV',
        'description': 'Mehrere Gemeinden der Region'
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
        
        missing_fields = []
        
        for field, value in required_fields.items():
            if not value:
                missing_fields.append(field)
            elif field == 'parishes' and len(value) == 0:
                missing_fields.append(field)
        
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
            start_date = datetime.fromisoformat(event['startDate'].replace('Z', '+00:00'))
            
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