#!/usr/bin/env python3
"""
Debug the arcs API to see what's being returned
"""

import requests
import json

def debug_arcs_api():
    """Debug the arcs API response"""
    
    try:
        print("🔍 Debugging arcs API...")
        print("=" * 50)
        
        # Test the API
        response = requests.get("http://localhost:5000/api/arcs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                arcs = data.get('data', [])
                print(f"📊 API returned {len(arcs)} arcs")
                
                # Check geometry data
                arcs_with_geom = [arc for arc in arcs if arc.get('geometrie')]
                arcs_without_geom = [arc for arc in arcs if not arc.get('geometrie')]
                
                print(f"✅ Arcs with geometry: {len(arcs_with_geom)}")
                print(f"❌ Arcs without geometry: {len(arcs_without_geom)}")
                
                # Show sample of arcs with geometry
                print(f"\n🔍 Sample arcs WITH geometry:")
                for i, arc in enumerate(arcs_with_geom[:5]):
                    arc_id = arc.get('id')
                    nom_axe = arc.get('axe')  # Note: API returns 'axe' not 'nom_axe'
                    geometrie = arc.get('geometrie')
                    print(f"   Arc {arc_id} ({nom_axe}): {geometrie[:100]}...")
                
                # Show sample of arcs without geometry
                print(f"\n❌ Sample arcs WITHOUT geometry:")
                for i, arc in enumerate(arcs_without_geom[:5]):
                    arc_id = arc.get('id')
                    nom_axe = arc.get('axe')
                    geometrie = arc.get('geometrie')
                    print(f"   Arc {arc_id} ({nom_axe}): {geometrie}")
                
                # Check if there are any arcs with null geometry
                arcs_with_null_geom = [arc for arc in arcs if arc.get('geometrie') is None]
                print(f"\n⚠️ Arcs with null geometry: {len(arcs_with_null_geom)}")
                
                # Show the first few arcs to see the structure
                print(f"\n📋 First 3 arcs structure:")
                for i, arc in enumerate(arcs[:3]):
                    print(f"   Arc {i+1}: {json.dumps(arc, indent=2, default=str)}")
                
            else:
                print(f"❌ API returned success=false: {data}")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_arcs_api()
