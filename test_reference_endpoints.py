#!/usr/bin/env python3
"""
Test simple des endpoints de référence
"""

import requests
import json

def test_reference_endpoints():
    """Tester les endpoints de référence"""
    
    print("🧪 Test des endpoints de référence")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # 1. Se connecter
        print("\n🔐 Authentification:")
        
        # Récupérer la page de connexion pour obtenir le CSRF token
        response = session.get(f"{base_url}/login")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        csrf_value = csrf_token['value']
        
        # Effectuer la connexion
        login_data = {
            'csrf_token': csrf_value,
            'username': 'admin',
            'password': 'admin123',
            'remember_me': 'y'
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        print("   ✅ Connexion réussie")
        
        # 2. Tester les endpoints
        print("\n🔗 Test des endpoints:")
        
        endpoints = [
            ('types', '/api/reference/types'),
            ('sous-types', '/api/reference/sous-types'),
            ('systemes', '/api/reference/systemes'),
            ('sources', '/api/reference/sources'),
            ('entites', '/api/reference/entites')
        ]
        
        for name, endpoint in endpoints:
            response = session.get(f"{base_url}{endpoint}")
            print(f"\n   📡 {name}:")
            print(f"      Status: {response.status_code}")
            print(f"      Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      Type de réponse: {type(data)}")
                    if isinstance(data, list):
                        print(f"      Nombre d'éléments: {len(data)}")
                        if data:
                            print(f"      Premier élément: {data[0]}")
                    elif isinstance(data, dict):
                        print(f"      Clés: {list(data.keys())}")
                        if 'error' in data:
                            print(f"      ❌ Erreur: {data['error']}")
                        if 'data' in data:
                            print(f"      Données: {len(data['data'])} éléments")
                        if 'success' in data:
                            print(f"      Succès: {data['success']}")
                    else:
                        print(f"      Contenu: {data}")
                except json.JSONDecodeError as e:
                    print(f"      ❌ Erreur JSON: {e}")
                    print(f"      Contenu brut: {response.text[:200]}...")
            else:
                print(f"      ❌ Erreur HTTP: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    from bs4 import BeautifulSoup
    test_reference_endpoints()
