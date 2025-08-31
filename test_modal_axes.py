import requests
import json
from bs4 import BeautifulSoup

def test_modal_axes():
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
        
        # 4. Récupérer les données des axes
        print("📡 Récupération des données des axes...")
        axes_response = session.get(f"{base_url}/api/axes?page=1&per_page=10")
        
        if axes_response.status_code == 200:
            data = axes_response.json()
            axes = data.get('data', [])
            
            if axes:
                # Prendre le premier axe pour le test
                test_axe = axes[0]
                print(f"✅ Axe de test: {test_axe.get('nom_axe')} (ID: {test_axe.get('id')})")
                
                # Simuler les données que le JavaScript utiliserait
                currentAxesData = axes
                
                # Simuler la fonction getCurrentAxesData
                def getCurrentAxesData():
                    return currentAxesData
                
                # Simuler la recherche d'un axe
                axe_id = test_axe.get('id')
                axe = next((a for a in getCurrentAxesData() if a.get('id') == axe_id), None)
                
                if axe:
                    print("✅ Axe trouvé dans les données actuelles")
                    print(f"   - Nom: {axe.get('nom_axe')}")
                    print(f"   - PK Début: {axe.get('pk_debut')}")
                    print(f"   - PK Fin: {axe.get('pk_fin')}")
                    print(f"   - PLOD: {axe.get('plod')}")
                    print(f"   - PLOF: {axe.get('plof')}")
                    print(f"   - ABSD: {axe.get('absd')}")
                    print(f"   - ABSF: {axe.get('absf')}")
                    print(f"   - Géométrie: {'Oui' if axe.get('geometrie') else 'Non'}")
                    
                    # Simuler l'affichage du modal
                    print("\n🎯 Simulation du modal des détails:")
                    print(f"   - Badge: Axe #{axe.get('axe_id', axe.get('id'))}")
                    print(f"   - Titre: {axe.get('nom_axe')}")
                    print(f"   - Description: Ligne ferroviaire")
                    print(f"   - PK Début: {axe.get('pk_debut', 'N/A')}")
                    print(f"   - PK Fin: {axe.get('pk_fin', 'N/A')}")
                    print(f"   - PLOD: {axe.get('plod', 'N/A')}")
                    print(f"   - PLOF: {axe.get('plof', 'N/A')}")
                    print(f"   - ABSD: {axe.get('absd', 'N/A')}")
                    print(f"   - ABSF: {axe.get('absf', 'N/A')}")
                    
                else:
                    print("❌ Axe non trouvé dans les données actuelles")
            else:
                print("❌ Aucun axe disponible")
        else:
            print(f"❌ Erreur API axes: {axes_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_modal_axes()
