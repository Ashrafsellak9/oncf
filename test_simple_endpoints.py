#!/usr/bin/env python3
"""
Test simple des endpoints API
"""

import requests
import json

def test_simple_endpoints():
    """Tester les endpoints API simplement"""
    
    print("🧪 Test simple des endpoints API")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # Test des endpoints de référence
        print("\n📚 Test des endpoints de référence:")
        
        endpoints = [
            '/api/reference/types',
            '/api/reference/sous-types', 
            '/api/reference/sources',
            '/api/reference/systemes',
            '/api/reference/entites',
            '/api/reference/localisations'
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      ✅ JSON valide: {len(data)} éléments")
                except:
                    print(f"      ⚠️ Réponse non-JSON")
            else:
                print(f"      ❌ Erreur {response.status_code}")
        
        # Test des incidents
        print("\n📋 Test des incidents:")
        response = requests.get(f"{base_url}/api/evenements?page=1&per_page=5")
        print(f"   /api/evenements: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                incidents = data.get('data', [])
                print(f"      ✅ {len(incidents)} incidents")
            except:
                print(f"      ⚠️ Réponse non-JSON")
        else:
            print(f"      ❌ Erreur {response.status_code}")
        
        # Test des statistiques
        print("\n📊 Test des statistiques:")
        response = requests.get(f"{base_url}/api/statistiques")
        print(f"   /api/statistiques: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"      ✅ Statistiques récupérées")
            except:
                print(f"      ⚠️ Réponse non-JSON")
        else:
            print(f"      ❌ Erreur {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_simple_endpoints()
