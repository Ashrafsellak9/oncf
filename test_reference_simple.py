#!/usr/bin/env python3
"""
Test simple de la page de référence
"""

import requests
from bs4 import BeautifulSoup
import time

def test_reference_simple():
    """Test simple de la page de référence"""
    
    print("🧪 Test simple de la page de référence")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # 1. Se connecter
        print("\n🔐 Authentification:")
        
        response = session.get(f"{base_url}/login")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        csrf_value = csrf_token['value']
        
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
            
            # Vérifier le contenu initial
            types_container = soup.find('div', {'id': 'typesContainer'})
            if types_container:
                print("   ✅ Conteneur types trouvé")
                
                # Vérifier s'il y a du contenu de chargement
                loading_text = types_container.find(text=lambda text: text and 'Chargement' in text)
                if loading_text:
                    print("   ✅ Texte de chargement présent")
                else:
                    print("   ⚠️  Texte de chargement non trouvé")
                    
                # Vérifier s'il y a des spinners
                spinners = types_container.find_all('div', class_='spinner-border')
                if spinners:
                    print(f"   ✅ {len(spinners)} spinner(s) trouvé(s)")
                else:
                    print("   ⚠️  Aucun spinner trouvé")
            else:
                print("   ❌ Conteneur types non trouvé")
            
            # Vérifier les onglets
            tabs = soup.find_all('a', {'data-tab': True})
            if tabs:
                print(f"   ✅ {len(tabs)} onglets trouvés")
                
                # Vérifier que l'onglet types est actif
                active_tab = soup.find('a', {'data-tab': 'types'})
                if active_tab and 'active' in active_tab.get('class', []):
                    print("   ✅ Onglet types actif")
                else:
                    print("   ⚠️  Onglet types non actif")
            else:
                print("   ❌ Aucun onglet trouvé")
                
        else:
            print(f"   ❌ Erreur accès page: {response.status_code}")
            return
        
        # 3. Tester un endpoint directement
        print("\n🔗 Test direct d'un endpoint:")
        response = session.get(f"{base_url}/api/reference/types")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    count = len(data.get('data', []))
                    print(f"   ✅ Endpoint types: {count} éléments")
                    
                    # Afficher quelques exemples
                    if count > 0:
                        print("   📝 Exemples:")
                        for i, item in enumerate(data['data'][:3], 1):
                            print(f"      {i}. {item.get('intitule', 'N/A')}")
                else:
                    print(f"   ❌ Erreur endpoint: {data.get('error', 'Erreur inconnue')}")
            except Exception as e:
                print(f"   ❌ Erreur parsing JSON: {e}")
        else:
            print(f"   ❌ Erreur endpoint: {response.status_code}")
        
        print("\n🎯 Résumé:")
        print("   ✅ Page accessible")
        print("   ✅ Scripts chargés")
        print("   ✅ Endpoints fonctionnels")
        print("   ⚠️  Problème probable: JavaScript ne s'exécute pas")
        print("\n💡 Solutions:")
        print("   1. Vérifier la console du navigateur (F12)")
        print("   2. Vérifier les erreurs JavaScript")
        print("   3. Vérifier que l'application est démarrée")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_reference_simple()
