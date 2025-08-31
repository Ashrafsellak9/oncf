import requests
import json
from bs4 import BeautifulSoup

def test_axes_api():
    # URL de base
    base_url = "http://localhost:5000"
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    
    try:
        # 1. Aller à la page de login
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
        print(f"✅ CSRF token extrait: {csrf_value[:20]}...")
        
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
        
        # 4. Tester l'API des axes
        print("📡 Test de l'API des axes...")
        axes_response = session.get(f"{base_url}/api/axes?page=1&per_page=10")
        
        print(f"Status code: {axes_response.status_code}")
        print(f"Headers: {dict(axes_response.headers)}")
        
        if axes_response.status_code == 200:
            try:
                data = axes_response.json()
                print("✅ API des axes fonctionne")
                print(f"📊 Total axes: {data.get('pagination', {}).get('total', 0)}")
                
                print("\n📋 Premiers axes:")
                for i, axe in enumerate(data.get('data', [])[:5]):
                    print(f"   {i+1}. ID: {axe.get('id')}, Nom: {axe.get('nom_axe')}, PK Début: {axe.get('pk_debut')}, PK Fin: {axe.get('pk_fin')}")
                    
                # Vérifier si les données sont correctes
                if data.get('data'):
                    first_axe = data['data'][0]
                    if first_axe.get('nom_axe') and first_axe['nom_axe'] != 'N/A':
                        print("✅ Les noms des axes sont correctement affichés !")
                    else:
                        print("❌ Les noms des axes ne s'affichent pas correctement")
                else:
                    print("❌ Aucune donnée d'axe reçue")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON: {e}")
                print(f"Réponse: {axes_response.text[:500]}...")
        else:
            print(f"❌ Erreur API axes: {axes_response.status_code}")
            print(axes_response.text[:500])
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_axes_api()
