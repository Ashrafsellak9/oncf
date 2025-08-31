import requests
import json

def test_axes_api():
    # URL de base
    base_url = "http://localhost:5000"
    
    # Test de l'API des axes
    print("🔍 Test de l'API des axes...")
    
    try:
        response = requests.get(f"{base_url}/api/axes?page=1&per_page=10")
        if response.status_code == 200:
            data = response.json()
            print("✅ API des axes fonctionne")
            print(f"📊 Total axes: {data.get('pagination', {}).get('total', 0)}")
            
            print("\n📋 Premiers axes:")
            for i, axe in enumerate(data.get('data', [])[:5]):
                print(f"   {i+1}. ID: {axe.get('id')}, Nom: {axe.get('nom_axe')}, PK Début: {axe.get('pk_debut')}, PK Fin: {axe.get('pk_fin')}")
        else:
            print(f"❌ Erreur API axes: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_axes_api()
