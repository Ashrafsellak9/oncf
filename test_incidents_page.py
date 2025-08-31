#!/usr/bin/env python3
"""
Test de la page des incidents après import
"""

import requests
import json
from bs4 import BeautifulSoup

def test_incidents_page():
    """Test de la page des incidents"""
    session = requests.Session()
    
    # Connexion
    print("🔐 Connexion...")
    try:
        response = session.get('http://localhost:5000/login')
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        csrf_value = csrf_token.get('value') if csrf_token else ""
        
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_value
        }
        
        response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("✅ Connexion réussie")
        else:
            print("❌ Échec de la connexion")
            return
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    # Test de la page des incidents
    print("\n📄 Test de la page des incidents...")
    try:
        response = session.get('http://localhost:5000/incidents')
        if response.status_code == 200:
            print("✅ Page des incidents accessible")
            
            # Vérifier le contenu
            if 'incidentsList' in response.text:
                print("✅ Conteneur incidentsList trouvé")
            else:
                print("❌ Conteneur incidentsList non trouvé")
                
            if 'incidents.js' in response.text:
                print("✅ Script incidents.js inclus")
            else:
                print("❌ Script incidents.js non inclus")
        else:
            print(f"❌ Erreur accès page incidents: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur page incidents: {e}")
    
    # Test de l'API des incidents
    print("\n🔌 Test de l'API des incidents...")
    try:
        response = session.get('http://localhost:5000/api/evenements?page=1&per_page=10')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API incidents accessible")
            print(f"   Total incidents: {data.get('total', 0)}")
            print(f"   Incidents dans la réponse: {len(data.get('incidents', []))}")
            
            if data.get('incidents'):
                incident = data['incidents'][0]
                print(f"   Premier incident: GID={incident.get('gid')}, Type={incident.get('type_id')}, Statut={incident.get('statut')}")
        else:
            print(f"❌ Erreur API incidents: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API incidents: {e}")
    
    # Test des statistiques
    print("\n📊 Test des statistiques...")
    try:
        response = session.get('http://localhost:5000/api/statistiques')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API statistiques accessible")
            print(f"   Total incidents: {data.get('total_incidents', 0)}")
            print(f"   Incidents ouverts: {data.get('incidents_ouverts', 0)}")
            print(f"   Incidents résolus: {data.get('incidents_resolus', 0)}")
        else:
            print(f"❌ Erreur API statistiques: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API statistiques: {e}")

if __name__ == "__main__":
    test_incidents_page() 