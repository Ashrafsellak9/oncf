#!/usr/bin/env python3
"""
Vérifier la géométrie complète des axes pour voir s'ils ont plus de points
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, GrapheArc, parse_wkt_linestring

def check_arc_full_geometry():
    """Vérifier la géométrie complète des axes"""
    with app.app_context():
        print("🔍 Vérification de la géométrie complète des axes...")
        
        # Récupérer quelques axes
        arcs = GrapheArc.query.limit(3).all()
        
        for arc in arcs:
            print(f"\n📍 Arc {arc.id}: {arc.nom_axe}")
            print(f"   Géométrie complète: {arc.geometrie}")
            
            # Parser la géométrie
            parsed = parse_wkt_linestring(arc.geometrie)
            if parsed:
                print(f"   Géométrie parsée: {parsed}")
                
                # Extraire les coordonnées pour vérification
                coords_str = parsed.replace('LINESTRING(', '').replace(')', '')
                points = coords_str.split(',')
                
                print(f"   Nombre de points: {len(points)}")
                
                # Afficher tous les points
                for i, point in enumerate(points):
                    coords = point.strip().split()
                    if len(coords) >= 2:
                        lon, lat = float(coords[0]), float(coords[1])
                        print(f"   Point {i+1}: Lon={lon:.6f}, Lat={lat:.6f}")
                
                # Calculer la distance totale
                if len(points) >= 2:
                    import math
                    total_distance = 0
                    for i in range(len(points) - 1):
                        coords1 = points[i].strip().split()
                        coords2 = points[i+1].strip().split()
                        if len(coords1) >= 2 and len(coords2) >= 2:
                            lon1, lat1 = float(coords1[0]), float(coords1[1])
                            lon2, lat2 = float(coords2[0]), float(coords2[1])
                            segment_distance = math.sqrt((lon2-lon1)**2 + (lat2-lat1)**2) * 111
                            total_distance += segment_distance
                    
                    print(f"   📏 Distance totale: {total_distance:.2f} km")
            else:
                print(f"   ❌ Échec du parsing de la géométrie")

if __name__ == "__main__":
    check_arc_full_geometry()
