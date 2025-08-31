#!/usr/bin/env python3
"""
Test script pour vérifier que l'API retourne les noms des références
"""

import requests

def test_api_names():
    """Tester que l'API retourne les noms des références"""
    
    print("🧪 Test de l'API avec noms des références")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000/api/evenements?page=1&per_page=3')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API répond correctement")
            print(f"Total incidents: {data['pagination']['total']}")
            
            for i, incident in enumerate(data['data']):
                print(f"\n   Incident {incident['id']}:")
                print(f"      Description: {incident['description'][:100]}...")
                print(f"      Type: {incident.get('type_name', 'N/A')} (ID: {incident['type_id']})")
                print(f"      Sous-type: {incident.get('sous_type_name', 'N/A')} (ID: {incident['sous_type_id']})")
                print(f"      Source: {incident.get('source_name', 'N/A')} (ID: {incident['source_id']})")
                print(f"      Système: {incident.get('system_name', 'N/A')}")
                print(f"      Entité: {incident.get('entite_name', 'N/A')}")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_api_names()
