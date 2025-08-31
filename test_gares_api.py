import requests
import json
from bs4 import BeautifulSoup

def test_gares_api():
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
        
        # 4. Tester l'API des gares
        print("📡 Test de l'API des gares...")
        gares_response = session.get(f"{base_url}/api/gares?page=1&per_page=10")
        
        print(f"Status code: {gares_response.status_code}")
        
        if gares_response.status_code == 200:
            try:
                data = gares_response.json()
                print("✅ API des gares fonctionne")
                print(f"📊 Total gares: {data.get('pagination', {}).get('total', 0)}")
                
                print("\n📋 Premières gares:")
                for i, gare in enumerate(data.get('data', [])[:5]):
                    print(f"   {i+1}. ID: {gare.get('id')}, Nom: {gare.get('nom')}, Code: {gare.get('code')}, Ville: {gare.get('ville')}")
                    
                # Vérifier si les données sont correctes
                if data.get('data'):
                    first_gare = data['data'][0]
                    if first_gare.get('nom') and first_gare['nom'] != 'N/A':
                        print("✅ Les noms des gares sont correctement affichés !")
                    else:
                        print("❌ Les noms des gares ne s'affichent pas correctement")
                else:
                    print("❌ Aucune donnée de gare reçue")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON: {e}")
                print(f"Réponse: {gares_response.text[:500]}...")
        else:
            print(f"❌ Erreur API gares: {gares_response.status_code}")
            print(gares_response.text[:500])
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_gares_api()
