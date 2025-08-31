import requests
import json
from bs4 import BeautifulSoup

def test_gares_web():
    # URL de base
    base_url = "http://localhost:5000"
    
    # Créer une session pour maintenir les cookies
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
        
        # 4. Accéder à la page des gares
        print("🏢 Accès à la page des gares...")
        gares_page = session.get(f"{base_url}/gares")
        
        if gares_page.status_code == 200:
            print("✅ Page des gares accessible")
            
            # 5. Tester l'API des gares avec pagination
            print("📡 Test de l'API des gares avec pagination...")
            gares_response = session.get(f"{base_url}/api/gares?page=1&per_page=25")
            
            if gares_response.status_code == 200:
                data = gares_response.json()
                print(f"✅ API des gares fonctionne")
                print(f"📊 Total gares: {data.get('pagination', {}).get('total', 0)}")
                print(f"📄 Page actuelle: {data.get('pagination', {}).get('page', 0)}")
                print(f"📋 Gares par page: {data.get('pagination', {}).get('per_page', 0)}")
                print(f"📊 Pages totales: {data.get('pagination', {}).get('pages', 0)}")
                
                if data.get('data'):
                    print(f"\n📋 Premières gares de la page:")
                    for i, gare in enumerate(data['data'][:5]):
                        print(f"   {i+1}. {gare.get('nom')} - {gare.get('code')} - {gare.get('ville')}")
                else:
                    print("❌ Aucune donnée de gare reçue")
            else:
                print(f"❌ Erreur API gares: {gares_response.status_code}")
        else:
            print(f"❌ Erreur page gares: {gares_page.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_gares_web()
