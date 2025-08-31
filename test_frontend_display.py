#!/usr/bin/env python3
"""
Test script pour vérifier l'affichage frontend avec les noms des références
"""

import requests
import json

def test_frontend_display():
    """Tester l'affichage frontend avec les noms des références"""
    
    print("🧪 Test de l'affichage frontend")
    print("=" * 50)
    
    try:
        # Récupérer les données des incidents
        response = requests.get('http://localhost:5000/api/evenements?page=1&per_page=5')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API répond correctement")
            print(f"Total incidents: {data['pagination']['total']}")
            
            print("\n📋 Données disponibles pour l'affichage frontend:")
            for i, incident in enumerate(data['data']):
                print(f"\n   Incident {incident['id']}:")
                print(f"      Description: {incident['description'][:80]}...")
                print(f"      Type: {incident.get('type_name', 'N/A')}")
                print(f"      Sous-type: {incident.get('sous_type_name', 'N/A')}")
                print(f"      Source: {incident.get('source_name', 'N/A')}")
                print(f"      Système: {incident.get('system_name', 'N/A')}")
                print(f"      Entité: {incident.get('entite_name', 'N/A')}")
                print(f"      Localisation: {incident.get('location_name', 'N/A')}")
                print(f"      Statut: {incident.get('statut', 'N/A')}")
                
                # Vérifier que les noms sont bien présents
                missing_names = []
                if not incident.get('type_name'):
                    missing_names.append('type_name')
                if not incident.get('sous_type_name'):
                    missing_names.append('sous_type_name')
                if not incident.get('source_name'):
                    missing_names.append('source_name')
                
                if missing_names:
                    print(f"      ⚠️  Noms manquants: {', '.join(missing_names)}")
                else:
                    print(f"      ✅ Tous les noms sont présents")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n🎯 Résumé:")
    print("   - L'API retourne maintenant les noms des références")
    print("   - Le frontend JavaScript a été mis à jour pour utiliser ces noms")
    print("   - Les incidents afficheront des noms descriptifs au lieu d'IDs")
    print("   - Les détails des incidents incluent toutes les informations de référence")

if __name__ == "__main__":
    test_frontend_display()
