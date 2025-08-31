#!/usr/bin/env python3
"""
Script pour tester tous les endpoints API
"""

import requests
import json

def test_api_endpoints():
    """Tester tous les endpoints API"""
    base_url = "http://localhost:5000"
    
    # Endpoints à tester
    endpoints = [
        "/api/gares",
        "/api/gares/filters", 
        "/api/evenements",
        "/api/types-incidents",
        "/api/localisations",
        "/api/statistiques",
        "/api/axes",
        "/api/reference/types",
        "/api/reference/sous-types",
        "/api/reference/systemes",
        "/api/reference/sources",
        "/api/reference/entites",
        "/api/statistics"
    ]
    
    print("🧪 Test des endpoints API...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            print(f"📡 Test de {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
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
    test_api_endpoints()
