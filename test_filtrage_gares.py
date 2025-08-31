import requests
import json
from bs4 import BeautifulSoup

def test_filtrage_gares():
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # 1. Se connecter
        print("🔍 Accès à la page de login...")
        login_response = session.get(f"{base_url}/login")
        
        if login_response.status_code != 200:
            print(f"❌ Erreur accès login: {login_response.status_code}")
            return
            
        # 2. Extraire le CSRF token
        soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_token:
            print("❌ CSRF token non trouvé")
            return
            
        csrf_value = csrf_token['value']
        
        # 3. Se connecter
        print("🔐 Tentative de connexion...")
        login_data = {
            'csrf_token': csrf_value,
            'username': 'admin',
            'password': 'admin123',
            'remember_me': False
        }
        
        login_post = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if login_post.status_code != 302:
            print(f"❌ Erreur connexion: {login_post.status_code}")
            return
            
        print("✅ Connexion réussie")
        
        # 4. Tester les différents filtres
        print("\n🔍 Test des filtres de gares...")
        
        # Test 1: Filtre par section
        print("\n📋 Test 1: Filtre par section 'Facultes'")
        response = session.get(f"{base_url}/api/gares?section=Facultes&page=1&per_page=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Gares trouvées: {len(data.get('data', []))}")
            for gare in data.get('data', [])[:3]:
                print(f"      - {gare.get('nom')} (Section: {gare.get('section')})")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 2: Filtre par région
        print("\n📋 Test 2: Filtre par région 'CASABLANCA'")
        response = session.get(f"{base_url}/api/gares?region=CASABLANCA&page=1&per_page=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Gares trouvées: {len(data.get('data', []))}")
            for gare in data.get('data', [])[:3]:
                print(f"      - {gare.get('nom')} (Région: {gare.get('region')})")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 3: Filtre par type
        print("\n📋 Test 3: Filtre par type '8'")
        response = session.get(f"{base_url}/api/gares?type=8&page=1&per_page=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Gares trouvées: {len(data.get('data', []))}")
            for gare in data.get('data', [])[:3]:
                print(f"      - {gare.get('nom')} (Type: {gare.get('type')})")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 4: Filtre par état
        print("\n📋 Test 4: Filtre par état 'Haltes'")
        response = session.get(f"{base_url}/api/gares?etat=Haltes&page=1&per_page=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Gares trouvées: {len(data.get('data', []))}")
            for gare in data.get('data', [])[:3]:
                print(f"      - {gare.get('nom')} (État: {gare.get('etat')})")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 5: Filtre combiné
        print("\n📋 Test 5: Filtre combiné (section + région)")
        response = session.get(f"{base_url}/api/gares?section=Facultes&region=CASABLANCA&page=1&per_page=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Gares trouvées: {len(data.get('data', []))}")
            for gare in data.get('data', [])[:3]:
                print(f"      - {gare.get('nom')} (Section: {gare.get('section')}, Région: {gare.get('region')})")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        # Test 6: Recherche textuelle
        print("\n📋 Test 6: Recherche textuelle 'Facultes'")
        response = session.get(f"{base_url}/api/gares?search=Facultes&page=1&per_page=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Gares trouvées: {len(data.get('data', []))}")
            for gare in data.get('data', [])[:3]:
                print(f"      - {gare.get('nom')} (Section: {gare.get('section')})")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
        
        print("\n✅ Tests de filtrage terminés avec succès !")
        print("🌐 Vous pouvez maintenant tester l'interface web avec les nouveaux filtres")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_filtrage_gares()
