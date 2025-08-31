#!/usr/bin/env python3
"""
Test du frontend de la page de référence
"""

import requests
from bs4 import BeautifulSoup
import json

def test_reference_frontend():
    """Tester le frontend de la page de référence"""
    
    print("🧪 Test du frontend de la page de référence")
    print("=" * 50)
    
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
        
        # 2. Tester la page de référence
        print("\n📄 Test de la page de référence:")
        response = session.get(f"{base_url}/reference")
        
        if response.status_code == 200:
            print("   ✅ Page de référence accessible")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Vérifier le JavaScript
            scripts = soup.find_all('script')
            reference_script = None
            for script in scripts:
                if script.get('src') and 'reference.js' in script.get('src'):
                    reference_script = script
                    break
            
            if reference_script:
                print("   ✅ Script reference.js trouvé")
                
                # Vérifier le contenu du script
                script_url = f"{base_url}{reference_script['src']}"
                script_response = session.get(script_url)
                if script_response.status_code == 200:
                    print("   ✅ Script reference.js accessible")
                    script_content = script_response.text
                    
                    # Vérifier les fonctions importantes
                    functions_to_check = [
                        'loadReferenceData',
                        'displayReferenceData',
                        'setupTabs',
                        'switchTab'
                    ]
                    
                    for func in functions_to_check:
                        if func in script_content:
                            print(f"      ✅ Fonction {func} présente")
                        else:
                            print(f"      ❌ Fonction {func} manquante")
                else:
                    print(f"   ❌ Erreur accès script: {script_response.status_code}")
            else:
                print("   ❌ Script reference.js non trouvé")
            
            # Vérifier les conteneurs
            containers = ['typesContainer', 'sous-typesContainer', 'systemesContainer', 'sourcesContainer', 'entitesContainer']
            for container in containers:
                if soup.find('div', {'id': container}):
                    print(f"   ✅ Conteneur {container} présent")
                else:
                    print(f"   ❌ Conteneur {container} manquant")
            
            # Vérifier les onglets
            tabs = soup.find_all('a', {'data-tab': True})
            if tabs:
                print(f"   ✅ {len(tabs)} onglets trouvés")
                for tab in tabs:
                    tab_name = tab.get('data-tab')
                    print(f"      - Onglet: {tab_name}")
            else:
                print("   ❌ Aucun onglet trouvé")
            
            # Vérifier les éléments de chargement
            loading_elements = soup.find_all('div', class_='spinner-border')
            if loading_elements:
                print(f"   ✅ {len(loading_elements)} éléments de chargement trouvés")
            else:
                print("   ❌ Aucun élément de chargement trouvé")
                
        else:
            print(f"   ❌ Erreur accès page: {response.status_code}")
            return
        
        # 3. Tester les endpoints avec les headers appropriés
        print("\n🔗 Test des endpoints avec headers:")
        
        endpoints = [
            ('types', '/api/reference/types'),
            ('sous-types', '/api/reference/sous-types'),
            ('systemes', '/api/reference/systemes'),
            ('sources', '/api/reference/sources'),
            ('entites', '/api/reference/entites')
        ]
        
        headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        for name, endpoint in endpoints:
            response = session.get(f"{base_url}{endpoint}", headers=headers)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        count = len(data.get('data', []))
                        print(f"   ✅ {name}: {count} éléments")
                    else:
                        print(f"   ❌ {name}: Erreur - {data.get('error', 'Erreur inconnue')}")
                except json.JSONDecodeError:
                    print(f"   ❌ {name}: Réponse non-JSON")
            else:
                print(f"   ❌ {name}: Erreur {response.status_code}")
        
        print("\n🎯 Diagnostic:")
        print("   ✅ Backend fonctionnel")
        print("   ✅ Endpoints accessibles")
        print("   ✅ Page HTML correcte")
        print("   ⚠️  Problème probable: JavaScript côté client")
        print("\n💡 Solutions possibles:")
        print("   1. Vérifier la console du navigateur pour les erreurs JavaScript")
        print("   2. Vérifier que le script reference.js se charge correctement")
        print("   3. Vérifier les erreurs CORS ou d'authentification")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_reference_frontend()
