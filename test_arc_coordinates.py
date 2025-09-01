#!/usr/bin/env python3
"""
Test des coordonnées des axes pour vérifier leur transformation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, GrapheArc, parse_wkt_linestring

def test_arc_coordinates():
    """Test des coordonnées des axes"""
    with app.app_context():
        print("🔍 Test des coordonnées des axes...")
        
        # Récupérer quelques axes
        arcs = GrapheArc.query.limit(5).all()
        
        for arc in arcs:
            print(f"\n📍 Arc {arc.id}: {arc.nom_axe}")
            print(f"   Géométrie originale: {arc.geometrie[:100]}...")
            
            # Parser la géométrie
            parsed = parse_wkt_linestring(arc.geometrie)
            if parsed:
                print(f"   Géométrie parsée: {parsed}")
                
                # Extraire les coordonnées pour vérification
                coords_str = parsed.replace('LINESTRING(', '').replace(')', '')
                points = coords_str.split(',')
                
                print(f"   Nombre de points: {len(points)}")
                
                # Afficher les premiers et derniers points
                if len(points) >= 2:
                    first_point = points[0].strip().split()
                    last_point = points[-1].strip().split()
                    
                    if len(first_point) >= 2 and len(last_point) >= 2:
                        lon1, lat1 = float(first_point[0]), float(first_point[1])
                        lon2, lat2 = float(last_point[0]), float(last_point[1])
                        
                        print(f"   Premier point: Lon={lon1:.6f}, Lat={lat1:.6f}")
                        print(f"   Dernier point: Lon={lon2:.6f}, Lat={lat2:.6f}")
                        
                        # Vérifier si les coordonnées sont dans les limites du Maroc
                        if -10 <= lon1 <= -1 and 27 <= lat1 <= 37:
                            print(f"   ✅ Premier point dans les limites du Maroc")
                        else:
                            print(f"   ⚠️ Premier point hors limites du Maroc")
                            
                        if -10 <= lon2 <= -1 and 27 <= lat2 <= 37:
                            print(f"   ✅ Dernier point dans les limites du Maroc")
                        else:
                            print(f"   ⚠️ Dernier point hors limites du Maroc")
                            
                        # Calculer la distance approximative
                        import math
                        distance = math.sqrt((lon2-lon1)**2 + (lat2-lat1)**2) * 111  # km approximatif
                        print(f"   📏 Distance approximative: {distance:.2f} km")
            else:
                print(f"   ❌ Échec du parsing de la géométrie")

if __name__ == "__main__":
    test_arc_coordinates()
