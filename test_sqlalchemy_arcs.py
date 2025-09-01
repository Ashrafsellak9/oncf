#!/usr/bin/env python3
"""
Test what SQLAlchemy is returning for the GrapheArc model
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sqlalchemy_arcs():
    """Test SQLAlchemy GrapheArc query"""
    
    try:
        # Import Flask app and models
        from app import app, GrapheArc, parse_wkt_linestring
        
        with app.app_context():
            print("🔍 Testing SQLAlchemy GrapheArc query...")
            print("=" * 50)
            
            # Test the same query as in api_arcs()
            arcs = GrapheArc.query.limit(50).all()
            print(f"📊 SQLAlchemy returned {len(arcs)} arcs")
            
            # Check geometry data
            arcs_with_geom = [arc for arc in arcs if arc.geometrie]
            arcs_without_geom = [arc for arc in arcs if not arc.geometrie]
            
            print(f"✅ Arcs with geometry: {len(arcs_with_geom)}")
            print(f"❌ Arcs without geometry: {len(arcs_without_geom)}")
            
            # Show sample of arcs with geometry
            print(f"\n🔍 Sample arcs WITH geometry:")
            for i, arc in enumerate(arcs_with_geom[:5]):
                print(f"   Arc {arc.id} ({arc.nom_axe}): {arc.geometrie[:100]}...")
                
                # Test parsing
                parsed = parse_wkt_linestring(arc.geometrie)
                if parsed:
                    print(f"      ✅ Parsed successfully: {parsed[:50]}...")
                else:
                    print(f"      ❌ Failed to parse")
            
            # Show sample of arcs without geometry
            print(f"\n❌ Sample arcs WITHOUT geometry:")
            for i, arc in enumerate(arcs_without_geom[:5]):
                print(f"   Arc {arc.id} ({arc.nom_axe}): {arc.geometrie}")
            
            # Check if there are any arcs with null geometry
            arcs_with_null_geom = [arc for arc in arcs if arc.geometrie is None]
            print(f"\n⚠️ Arcs with null geometry: {len(arcs_with_null_geom)}")
            
            # Show the first few arcs to see the structure
            print(f"\n📋 First 3 arcs structure:")
            for i, arc in enumerate(arcs[:3]):
                print(f"   Arc {i+1}: ID={arc.id}, nom_axe={arc.nom_axe}, geometrie={'Yes' if arc.geometrie else 'No'}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the oncf-ems directory")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_sqlalchemy_arcs()
