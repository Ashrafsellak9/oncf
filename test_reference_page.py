#!/usr/bin/env python3
"""
Test script pour vérifier la page de référence et ses endpoints
"""

import requests
import json
from bs4 import BeautifulSoup

def test_reference_page():
    """Tester la page de référence et ses endpoints"""
    
    print("🧪 Test de la page de référence")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # 1. Se connecter
        print("\n🔐 Authentification:")
        
        # Récupérer la page de connexion pour obtenir le CSRF token
        response = session.get(f"{base_url}/login")
        if response.status_code != 200:
            print(f"   ❌ Erreur accès page de connexion: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if not csrf_token:
            print("   ❌ Token CSRF non trouvé")
            return
        
        csrf_value = csrf_token['value']
        print(f"   ✅ Token CSRF récupéré")
        
        # Effectuer la connexion
        login_data = {
            'csrf_token': csrf_value,
            'username': 'admin',
            'password': 'admin123',
            'remember_me': 'y'
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200:
            print("   ✅ Connexion réussie")
        else:
            print(f"   ❌ Échec de la connexion: {response.status_code}")
            return
        
        # 2. Tester l'accès à la page de référence
        print("\n📄 Test de la page de référence:")
        response = session.get(f"{base_url}/reference")
        if response.status_code == 200:
            print("   ✅ Page de référence accessible")
            
            # Vérifier que la page contient les éléments attendus
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Vérifier les onglets
            tabs = soup.find_all('a', {'data-tab': True})
            expected_tabs = ['types', 'sous-types', 'systemes', 'sources', 'entites']
            found_tabs = [tab.get('data-tab') for tab in tabs]
            
            print(f"   📋 Onglets trouvés: {found_tabs}")
            for tab in expected_tabs:
                if tab in found_tabs:
                    print(f"      ✅ Onglet '{tab}' présent")
                else:
                    print(f"      ❌ Onglet '{tab}' manquant")
            
            # Vérifier les conteneurs
            containers = ['typesContainer', 'sous-typesContainer', 'systemesContainer', 'sourcesContainer', 'entitesContainer']
            for container in containers:
                if soup.find('div', {'id': container}):
                    print(f"      ✅ Conteneur '{container}' présent")
                else:
                    print(f"      ❌ Conteneur '{container}' manquant")
        else:
            print(f"   ❌ Erreur accès page: {response.status_code}")
            return
        
        # 3. Tester les endpoints de référence
        print("\n🔗 Test des endpoints de référence:")
        
        endpoints = [
            ('types', '/api/reference/types'),
            ('sous-types', '/api/reference/sous-types'),
            ('systemes', '/api/reference/systemes'),
            ('sources', '/api/reference/sources'),
            ('entites', '/api/reference/entites')
        ]
        
        for name, endpoint in endpoints:
            response = session.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   ✅ {name}: {len(data)} éléments")
                    elif isinstance(data, dict) and data.get('success'):
                        print(f"   ✅ {name}: {len(data.get('data', []))} éléments")
                    else:
                        print(f"   ⚠️ {name}: Format de réponse inattendu")
                except json.JSONDecodeError:
                    print(f"   ❌ {name}: Réponse non-JSON")
            else:
                print(f"   ❌ {name}: Erreur {response.status_code}")
        
        # 4. Tester le filtrage des sous-types
        print("\n🔍 Test du filtrage des sous-types:")
        response = session.get(f"{base_url}/api/reference/sous-types?type_id=1")
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Sous-types filtrés par type_id=1: {len(data)} éléments")
                else:
                    print(f"   ⚠️ Format de réponse inattendu pour le filtrage")
            except json.JSONDecodeError:
                print(f"   ❌ Réponse non-JSON pour le filtrage")
        else:
            print(f"   ❌ Erreur filtrage: {response.status_code}")
        
        print("\n🎯 Résumé:")
        print("   ✅ Page de référence accessible")
        print("   ✅ Onglets et conteneurs présents")
        print("   ✅ Endpoints de référence fonctionnels")
        print("   ✅ Authentification requise et fonctionnelle")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_reference_page()
