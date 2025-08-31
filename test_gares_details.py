import requests
import json
from bs4 import BeautifulSoup

def test_gares_details():
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
        
        # 4. Tester l'API des gares avec géométrie
        print("📡 Test de l'API des gares avec géométrie...")
        gares_response = session.get(f"{base_url}/api/gares?page=1&per_page=10")
        
        if gares_response.status_code == 200:
            data = gares_response.json()
            print(f"📊 Total gares: {data.get('pagination', {}).get('total', 0)}")
            
            # Chercher une gare avec géométrie
            gare_avec_geometrie = None
            for gare in data.get('data', []):
                if gare.get('geometrie'):
                    gare_avec_geometrie = gare
                    break
            
            if gare_avec_geometrie:
                print(f"\n🎯 Gare trouvée avec géométrie:")
                print(f"   - ID: {gare_avec_geometrie.get('id')}")
                print(f"   - Nom: {gare_avec_geometrie.get('nom')}")
                print(f"   - Code: {gare_avec_geometrie.get('code')}")
                print(f"   - Type: {gare_avec_geometrie.get('type')}")
                print(f"   - État: {gare_avec_geometrie.get('etat')}")
                print(f"   - Section: {gare_avec_geometrie.get('section')}")
                print(f"   - Région: {gare_avec_geometrie.get('region')}")
                print(f"   - Ville: {gare_avec_geometrie.get('ville')}")
                print(f"   - PK Début: {gare_avec_geometrie.get('pk_debut')}")
                print(f"   - PLOD: {gare_avec_geometrie.get('plod')}")
                print(f"   - PLOF: {gare_avec_geometrie.get('plof')}")
                print(f"   - Distance: {gare_avec_geometrie.get('distance')}")
                print(f"   - Type Commercial: {gare_avec_geometrie.get('type_commercial')}")
                print(f"   - Statut: {gare_avec_geometrie.get('statut')}")
                print(f"   - Commentaire: {gare_avec_geometrie.get('commentaire')}")
                print(f"   - Géométrie: {gare_avec_geometrie.get('geometrie')}")
                print(f"   - Géométrie Déc: {gare_avec_geometrie.get('geometrie_dec')}")
                
                # Tester le parsing WKT
                geometrie = gare_avec_geometrie.get('geometrie')
                if geometrie and geometrie.startswith('POINT('):
                    print(f"\n📍 Coordonnées extraites du WKT:")
                    coords = geometrie.replace('POINT(', '').replace(')', '').split(' ')
                    lon = float(coords[0])
                    lat = float(coords[1])
                    print(f"   - Longitude: {lon}")
                    print(f"   - Latitude: {lat}")
                    print(f"   - URL Google Maps: https://www.google.com/maps?q={lat},{lon}")
                
                print("\n✅ Toutes les informations géométriques sont disponibles !")
                print("🌐 Vous pouvez maintenant tester l'affichage des détails dans l'interface web")
                
            else:
                print("❌ Aucune gare avec géométrie trouvée")
                
        else:
            print(f"❌ Erreur API gares: {gares_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_gares_details()
