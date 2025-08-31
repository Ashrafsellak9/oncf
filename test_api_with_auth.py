#!/usr/bin/env python3
"""
Script pour tester les endpoints API avec authentification
"""

import requests
import json

def test_api_with_auth():
    """Tester les endpoints API avec authentification"""
    base_url = "http://localhost:5000"
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    
    # Données de connexion
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'remember_me': False
    }
    
    print("🔐 Connexion à l'application...")
    
    try:
        # Se connecter
        login_response = session.post(f"{base_url}/login", data=login_data, timeout=10)
        
        if login_response.status_code == 200:
            print("✅ Connexion réussie")
        else:
            print(f"❌ Échec de la connexion: {login_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    # Endpoints à tester (ceux qui nécessitent une authentification)
    protected_endpoints = [
        "/api/axes",
        "/api/reference/types",
        "/api/reference/sous-types", 
        "/api/reference/systemes",
        "/api/reference/sources",
        "/api/reference/entites",
        "/api/statistics"
    ]
    
    print("\n🧪 Test des endpoints protégés...")
    print("=" * 50)
    
    for endpoint in protected_endpoints:
        try:
            print(f"📡 Test de {endpoint}...")
            response = session.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ {endpoint} - Succès")
                        if 'data' in data:
                            if isinstance(data['data'], list):
                                print(f"   📊 {len(data['data'])} éléments")
                            elif isinstance(data['data'], dict):
                                print(f"   📊 Données reçues")
                    else:
                        print(f"❌ {endpoint} - Erreur: {data.get('error', 'Erreur inconnue')}")
                except json.JSONDecodeError:
                    print(f"❌ {endpoint} - Réponse non-JSON: {response.text[:100]}")
            else:
                print(f"❌ {endpoint} - Code HTTP: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Impossible de se connecter au serveur")
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint} - Timeout")
        except Exception as e:
            print(f"❌ {endpoint} - Erreur: {e}")
        
        print("-" * 30)
    
    print("🎯 Test terminé!")

if __name__ == "__main__":
    test_api_with_auth()
