#!/usr/bin/env python3
"""
Test de la nouvelle API des arcs qui combine les segments
"""

import requests
import json

def test_arcs_api():
    """Test de l'API des arcs"""
    print("🔍 Test de l'API des arcs combinés...")
    
    try:
        response = requests.get('http://localhost:5000/api/arcs')
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                arcs = data.get('data', [])
                print(f"✅ {len(arcs)} axes combinés récupérés")
                
                for arc in arcs[:3]:  # Afficher les 3 premiers
                    print(f"\n📍 Axe: {arc['axe']}")
                    print(f"   ID: {arc['id']}")
                    print(f"   Nombre de segments: {arc.get('nombre_segments', 'N/A')}")
                    print(f"   PK Début: {arc.get('pk_debut', 'N/A')}")
                    print(f"   PK Fin: {arc.get('pk_fin', 'N/A')}")
                    
                    # Vérifier la géométrie
                    geometrie = arc.get('geometrie', '')
                    if geometrie:
                        coords_str = geometrie.replace('LINESTRING(', '').replace(')', '')
                        points = coords_str.split(',')
                        print(f"   Nombre de points: {len(points)}")
                        
                        # Calculer la distance approximative
                        if len(points) >= 2:
                            import math
                            first_point = points[0].strip().split()
                            last_point = points[-1].strip().split()
                            
                            if len(first_point) >= 2 and len(last_point) >= 2:
                                lon1, lat1 = float(first_point[0]), float(first_point[1])
                                lon2, lat2 = float(last_point[0]), float(last_point[1])
                                
                                distance = math.sqrt((lon2-lon1)**2 + (lat2-lat1)**2) * 111
                                print(f"   📏 Distance totale: {distance:.2f} km")
                                
                                print(f"   Premier point: Lon={lon1:.6f}, Lat={lat1:.6f}")
                                print(f"   Dernier point: Lon={lon2:.6f}, Lat={lat2:.6f}")
                    else:
                        print(f"   ❌ Pas de géométrie")
            else:
                print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_arcs_api()
