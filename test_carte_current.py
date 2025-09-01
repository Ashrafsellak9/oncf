#!/usr/bin/env python3
"""
Test script to debug carte interactive issues
"""

import requests
import json
import sys

def test_api_endpoint(url, name):
    """Test an API endpoint and return the response"""
    try:
        print(f"\n🔍 Testing {name}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name} - Status: {response.status_code}")
            
            if 'data' in data:
                if isinstance(data['data'], list):
                    print(f"   📊 {len(data['data'])} items found")
                    if data['data']:
                        print(f"   📋 First item keys: {list(data['data'][0].keys())}")
                        # Show first item for debugging
                        print(f"   🔍 First item: {json.dumps(data['data'][0], indent=2, default=str)}")
                else:
                    print(f"   📊 Data structure: {type(data['data'])}")
                    print(f"   📋 Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'N/A'}")
            else:
                print(f"   📊 Response structure: {list(data.keys())}")
            
            return data
        else:
            print(f"❌ {name} - Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ {name} - Error: {str(e)}")
        return None

def main():
    base_url = "http://localhost:5000"
    
    print("🚀 Testing Carte Interactive APIs...")
    print("=" * 50)
    
    # Test gares API
    gares_data = test_api_endpoint(f"{base_url}/api/gares", "Gares API")
    
    # Test arcs API
    arcs_data = test_api_endpoint(f"{base_url}/api/arcs", "Arcs API")
    
    # Test incidents API with per_page=1000
    incidents_data = test_api_endpoint(f"{base_url}/api/evenements?per_page=1000", "Incidents API (all)")
    
    # Test incidents API with normal pagination
    incidents_paged_data = test_api_endpoint(f"{base_url}/api/evenements?page=1&per_page=50", "Incidents API (paged)")
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    
    if gares_data and 'data' in gares_data:
        gares_count = len(gares_data['data']) if isinstance(gares_data['data'], list) else 0
        print(f"   🚉 Gares: {gares_count}")
    
    if arcs_data and 'data' in arcs_data:
        arcs_count = len(arcs_data['data']) if isinstance(arcs_data['data'], list) else 0
        print(f"   🛤️  Arcs: {arcs_count}")
    
    if incidents_data and 'data' in incidents_data:
        incidents_count = len(incidents_data['data']) if isinstance(incidents_data['data'], list) else 0
        print(f"   🚨 Incidents (all): {incidents_count}")
    
    if incidents_paged_data and 'data' in incidents_paged_data:
        incidents_paged_count = len(incidents_paged_data['data']) if isinstance(incidents_paged_data['data'], list) else 0
        print(f"   🚨 Incidents (paged): {incidents_paged_count}")
    
    print("\n🔧 DEBUGGING TIPS:")
    print("1. Check browser console for JavaScript errors")
    print("2. Verify Flask app is running on port 5000")
    print("3. Check database connection and data")
    print("4. Look for geometry parsing issues")

if __name__ == "__main__":
    main()
