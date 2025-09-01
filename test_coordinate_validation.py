#!/usr/bin/env python3
"""
Test which arcs are failing coordinate validation
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_coordinate_validation():
    """Test coordinate validation for all arcs"""
    
    try:
        # Import Flask app and models
        from app import app, GrapheArc, parse_wkt_linestring
        
        with app.app_context():
            print("🔍 Testing coordinate validation for all arcs...")
            print("=" * 50)
            
            # Get all arcs
            arcs = GrapheArc.query.limit(50).all()
            print(f"📊 Testing {len(arcs)} arcs")
            
            successful_parses = 0
            failed_parses = 0
            
            for arc in arcs:
                print(f"\nArc {arc.id} ({arc.nom_axe}):")
                
                if not arc.geometrie:
                    print(f"   ❌ No geometry data")
                    failed_parses += 1
                    continue
                
                # Test parsing
                parsed = parse_wkt_linestring(arc.geometrie)
                
                if parsed:
                    print(f"   ✅ Parsed successfully: {parsed[:50]}...")
                    successful_parses += 1
                else:
                    print(f"   ❌ Failed to parse")
                    print(f"   Raw geometry: {arc.geometrie[:100]}...")
                    failed_parses += 1
                    
                    # Let's manually test the coordinate conversion
                    try:
                        from pyproj import Transformer
                        
                        # Extract coordinates manually
                        if 'SRID=3857;LINESTRING(' in arc.geometrie:
                            coords_str = arc.geometrie.split('LINESTRING(')[1].rstrip(')')
                            
                            # Test first point
                            first_point = coords_str.split(',')[0].strip()
                            x, y = map(float, first_point.split())
                            
                            transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
                            lon, lat = transformer.transform(x, y)
                            
                            print(f"   First point conversion: ({x}, {y}) -> ({lon:.6f}, {lat:.6f})")
                            
                            if not (-10 <= lon <= -1 and 27 <= lat <= 37):
                                print(f"   ❌ Point outside Morocco bounds: Lon={lon:.6f}, Lat={lat:.6f}")
                            else:
                                print(f"   ✅ Point within Morocco bounds")
                                
                    except Exception as e:
                        print(f"   Error in manual conversion: {e}")
            
            print(f"\n📊 Summary:")
            print(f"   Successful parses: {successful_parses}")
            print(f"   Failed parses: {failed_parses}")
            print(f"   Success rate: {successful_parses/(successful_parses+failed_parses)*100:.1f}%")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the oncf-ems directory")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_coordinate_validation()
