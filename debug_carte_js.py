#!/usr/bin/env python3
"""
Debug script for carte interactive JavaScript issues
"""

import requests
import json
import time

def test_carte_page():
    """Test the carte page and check for JavaScript errors"""
    print("🔍 Testing carte page...")
    
    try:
        # Test the carte page
        response = requests.get("http://localhost:5000/carte", timeout=10)
        
        if response.status_code == 200:
            print("✅ Carte page accessible")
            
            # Check if the page contains necessary elements
            content = response.text
            
            # Check for JavaScript files
            if 'carte.js' in content:
                print("✅ carte.js referenced in page")
            else:
                print("❌ carte.js not found in page")
            
            # Check for Leaflet
            if 'leaflet' in content.lower():
                print("✅ Leaflet referenced in page")
            else:
                print("❌ Leaflet not found in page")
            
            # Check for map container
            if 'id="map"' in content:
                print("✅ Map container found")
            else:
                print("❌ Map container not found")
                
            # Check for extra_js block
            if '{% block extra_js %}' in content:
                print("✅ extra_js block found")
            else:
                print("❌ extra_js block not found")
                
        else:
            print(f"❌ Carte page error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing carte page: {str(e)}")

def test_api_responses():
    """Test API responses and check data structure"""
    print("\n🔍 Testing API responses...")
    
    apis = [
        ("/api/gares", "Gares"),
        ("/api/arcs", "Arcs"), 
        ("/api/evenements?per_page=1000", "Incidents")
    ]
    
    for api_url, name in apis:
        try:
            response = requests.get(f"http://localhost:5000{api_url}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    items = data.get('data', [])
                    print(f"✅ {name}: {len(items)} items")
                    
                    # Check for geometry in first item
                    if items and len(items) > 0:
                        first_item = items[0]
                        if 'geometrie' in first_item:
                            geom = first_item['geometrie']
                            if geom and geom != 'null':
                                print(f"   📍 {name} geometry: {geom[:50]}...")
                            else:
                                print(f"   ❌ {name} geometry is null/empty")
                        else:
                            print(f"   ❌ {name} no geometry field")
                else:
                    print(f"❌ {name}: API returned success=false")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")

def test_geometry_parsing():
    """Test geometry parsing with sample data"""
    print("\n🔍 Testing geometry parsing...")
    
    # Sample geometries from our API test
    test_geometries = [
        "POINT(-7.65002376331154 33.54116657013629)",  # Gare
        "LINESTRING(-7.65002376331154 33.54116657013629,-7.650121888857212 33.541232135541264)",  # Arc
        "POINT(-4.0167 34.2167)"  # Incident
    ]
    
    for i, geom in enumerate(test_geometries):
        print(f"   Test {i+1}: {geom}")
        
        # Test POINT parsing
        if geom.startswith('POINT'):
            import re
            match = re.match(r'POINT\(([^)]+)\)', geom)
            if match:
                coords = match.group(1).split(' ')
                lng, lat = float(coords[0]), float(coords[1])
                print(f"      ✅ Parsed: [{lat}, {lng}]")
            else:
                print(f"      ❌ Failed to parse POINT")
        
        # Test LINESTRING parsing  
        elif geom.startswith('LINESTRING'):
            import re
            match = re.match(r'LINESTRING\(([^)]+)\)', geom)
            if match:
                coords_str = match.group(1)
                coords = []
                for coord_pair in coords_str.split(','):
                    lng, lat = coord_pair.strip().split(' ')
                    coords.append([float(lat), float(lng)])
                print(f"      ✅ Parsed: {len(coords)} points")
            else:
                print(f"      ❌ Failed to parse LINESTRING")

def main():
    print("🚀 Debugging Carte Interactive Issues")
    print("=" * 50)
    
    test_carte_page()
    test_api_responses()
    
    print("\n🔧 DEBUGGING INSTRUCTIONS:")
    print("1. Open browser console (F12)")
    print("2. Go to http://localhost:5000/carte")
    print("3. Check for JavaScript errors")
    print("4. Look for these console messages:")
    print("   - '🔄 Chargement de tous les incidents...'")
    print("   - '✅ X incidents chargés au total'")
    print("   - '🗺️ Ajout de X incidents à la carte...'")
    print("   - '✅ X incidents ajoutés à la carte'")
    print("5. Check if map layers are created:")
    print("   - garesLayer, arcsLayer, incidentsLayer")
    print("6. Verify geometry parsing is working")

if __name__ == "__main__":
    main()
