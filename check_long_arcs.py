#!/usr/bin/env python3
"""
Vérifier les arcs avec des géométries plus longues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, GrapheArc, parse_wkt_linestring

def check_long_arcs():
    """Vérifier les arcs avec des géométries plus longues"""
    with app.app_context():
        print("🔍 Vérification des arcs avec des géométries longues...")
        
        arcs = GrapheArc.query.all()
        
        # Analyser chaque arc
        arc_details = []
        for arc in arcs:
            if arc.geometrie:
                parsed = parse_wkt_linestring(arc.geometrie)
                if parsed:
                    coords_str = parsed.replace('LINESTRING(', '').replace(')', '')
                    points = coords_str.split(',')
                    point_count = len(points)
                    
                    # Calculer la distance approximative
                    if len(points) >= 2:
                        import math
                        first_point = points[0].strip().split()
                        last_point = points[-1].strip().split()
                        if len(first_point) >= 2 and len(last_point) >= 2:
                            lon1, lat1 = float(first_point[0]), float(first_point[1])
                            lon2, lat2 = float(last_point[0]), float(last_point[1])
                            distance = math.sqrt((lon2-lon1)**2 + (lat2-lat1)**2) * 111
                        else:
                            distance = 0
                    else:
                        distance = 0
                    
                    arc_details.append({
                        'id': arc.id,
                        'nom_axe': arc.nom_axe,
                        'point_count': point_count,
                        'distance': distance,
                        'pk_debut': arc.pk_debut,
                        'pk_fin': arc.pk_fin
                    })
        
        # Trier par nombre de points (décroissant)
        arc_details.sort(key=lambda x: x['point_count'], reverse=True)
        
        print(f"\n📊 Top 10 des arcs avec le plus de points:")
        for i, arc in enumerate(arc_details[:10]):
            print(f"{i+1}. {arc['nom_axe']} (ID: {arc['id']})")
            print(f"   Points: {arc['point_count']}, Distance: {arc['distance']:.2f} km")
            print(f"   PK: {arc['pk_debut']} - {arc['pk_fin']}")
            print()
        
        # Trier par distance (décroissant)
        arc_details.sort(key=lambda x: x['distance'], reverse=True)
        
        print(f"\n📏 Top 10 des arcs les plus longs:")
        for i, arc in enumerate(arc_details[:10]):
            print(f"{i+1}. {arc['nom_axe']} (ID: {arc['id']})")
            print(f"   Distance: {arc['distance']:.2f} km, Points: {arc['point_count']}")
            print(f"   PK: {arc['pk_debut']} - {arc['pk_fin']}")
            print()

if __name__ == "__main__":
    check_long_arcs()
