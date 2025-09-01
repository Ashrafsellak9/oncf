#!/usr/bin/env python3
"""
Debug des coordonnées pour comprendre le problème de transformation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, GrapheArc, parse_wkt_linestring
import pyproj

def debug_coordinates():
    """Debug des coordonnées"""
    with app.app_context():
        print("🔍 Debug des coordonnées...")
        
        # Prendre un arc avec beaucoup de points
        arc = GrapheArc.query.filter_by(id=11).first()  # LGV_V2
        if not arc:
            print("❌ Arc non trouvé")
            return
            
        print(f"📍 Arc: {arc.nom_axe} (ID: {arc.id})")
        print(f"   Géométrie originale: {arc.geometrie[:200]}...")
        
        # Parser la géométrie
        parsed = parse_wkt_linestring(arc.geometrie)
        if parsed:
            print(f"   Géométrie parsée: {parsed[:200]}...")
            
            coords_str = parsed.replace('LINESTRING(', '').replace(')', '')
            points = coords_str.split(',')
            
            print(f"\n📊 Analyse des coordonnées:")
            print(f"   Nombre de points: {len(points)}")
            
            # Afficher les premiers points
            for i, point in enumerate(points[:5]):
                coords = point.strip().split()
                if len(coords) >= 2:
                    lon, lat = float(coords[0]), float(coords[1])
                    print(f"   Point {i+1}: Lon={lon:.6f}, Lat={lat:.6f}")
                    
                    # Vérifier si les coordonnées sont dans les limites du Maroc
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        print(f"      ✅ Dans les limites du Maroc")
                    else:
                        print(f"      ⚠️ Hors des limites du Maroc")
            
            # Afficher les derniers points
            print(f"\n   Derniers points:")
            for i, point in enumerate(points[-5:]):
                coords = point.strip().split()
                if len(coords) >= 2:
                    lon, lat = float(coords[0]), float(coords[1])
                    print(f"   Point {len(points)-4+i}: Lon={lon:.6f}, Lat={lat:.6f}")
                    
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        print(f"      ✅ Dans les limites du Maroc")
                    else:
                        print(f"      ⚠️ Hors des limites du Maroc")
            
            # Calculer la distance réelle
            if len(points) >= 2:
                import math
                first_point = points[0].strip().split()
                last_point = points[-1].strip().split()
                if len(first_point) >= 2 and len(last_point) >= 2:
                    lon1, lat1 = float(first_point[0]), float(first_point[1])
                    lon2, lat2 = float(last_point[0]), float(last_point[1])
                    distance = math.sqrt((lon2-lon1)**2 + (lat2-lat1)**2) * 111
                    print(f"\n📏 Distance calculée: {distance:.2f} km")
                    
                    # Vérifier si c'est réaliste pour le Maroc
                    if distance > 2000:
                        print(f"   ⚠️ Distance trop longue pour le Maroc (réseau total ~2000 km)")
                    elif distance > 500:
                        print(f"   ⚠️ Distance très longue pour une ligne")
                    else:
                        print(f"   ✅ Distance réaliste")

if __name__ == "__main__":
    debug_coordinates()
