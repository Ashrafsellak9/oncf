#!/usr/bin/env python3
"""
Test direct de l'API des incidents
"""

import requests
import json
from bs4 import BeautifulSoup

def test_api_direct():
    """Test direct de l'API"""
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
    
    # Test direct de l'API
    print("\n🔌 Test direct de l'API...")
    try:
        response = session.get('http://localhost:5000/api/evenements?page=1&per_page=10')
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Réponse JSON: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"❌ Réponse non-JSON: {response.text[:500]}")
        else:
            print(f"❌ Erreur HTTP: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Erreur API: {e}")
    
    # Test des statistiques
    print("\n📊 Test des statistiques...")
    try:
        response = session.get('http://localhost:5000/api/statistiques')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Statistiques: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"❌ Réponse non-JSON: {response.text[:500]}")
        else:
            print(f"❌ Erreur HTTP: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")

if __name__ == "__main__":
    test_api_direct()
