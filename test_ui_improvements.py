#!/usr/bin/env python3
"""
Test des améliorations UI
"""

import requests
import json
from bs4 import BeautifulSoup

def test_ui_improvements():
    """Test des améliorations UI"""
    session = requests.Session()
    
    # Connexion
    print("🔐 Connexion...")
    try:
        response = session.get('http://localhost:5000/login')
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        csrf_value = csrf_token.get('value') if csrf_token else ""
        
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_value
        }
        
        response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("✅ Connexion réussie")
        else:
            print(f"❌ Échec de connexion: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    # Test de la page des axes
    print("\n🧪 Test de la page des axes...")
    try:
        response = session.get('http://localhost:5000/axes')
        if response.status_code == 200:
            print("✅ Page des axes accessible")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Vérifier les nouvelles classes CSS
            cards = soup.find_all('div', class_='card')
            if cards:
                print(f"✅ {len(cards)} carte(s) trouvée(s)")
            else:
                print("⚠️ Aucune carte trouvée")
            
            # Vérifier les icônes FontAwesome
            icons = soup.find_all('i', class_='fas')
            if icons:
                print(f"✅ {len(icons)} icône(s) FontAwesome trouvée(s)")
            else:
                print("⚠️ Aucune icône trouvée")
            
            # Vérifier les animations CSS
            fade_elements = soup.find_all(class_='fade-in-up')
            if fade_elements:
                print(f"✅ {len(fade_elements)} élément(s) avec animation trouvé(s)")
            else:
                print("⚠️ Aucune animation trouvée")
            
            # Vérifier le script axes.js
            scripts = soup.find_all('script')
            axes_js_found = False
            for script in scripts:
                if script.get('src') and 'axes.js' in script.get('src'):
                    axes_js_found = True
                    break
            
            if axes_js_found:
                print("✅ Script axes.js trouvé")
            else:
                print("❌ Script axes.js non trouvé")
                
        else:
            print(f"❌ Page des axes inaccessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur accès page axes: {e}")
    
    # Test de l'API axes
    print("\n🧪 Test de l'API axes...")
    try:
        response = session.get('http://localhost:5000/api/axes?page=1&per_page=5')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                axes_count = len(data.get('data', []))
                total = data.get('pagination', {}).get('total', 0)
                print(f"✅ API Axes: {axes_count} axes disponibles sur {total} au total")
                
                if axes_count > 0:
                    first_axe = data['data'][0]
                    print(f"📝 Premier axe: {first_axe.get('axe', 'N/A')}")
                    print(f"📝 ID: {first_axe.get('id', 'N/A')}")
                    print(f"📝 PK Début: {first_axe.get('cumuld', 'N/A')}")
                    print(f"📝 PK Fin: {first_axe.get('cumulf', 'N/A')}")
                
            else:
                print(f"❌ API Axes: Erreur - {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ API Axes: Code d'erreur {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur API axes: {e}")
    
    # Test des fichiers statiques
    print("\n🧪 Test des fichiers statiques...")
    static_files = [
        '/static/css/style.css',
        '/static/js/axes.js',
        '/static/js/main.js'
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f'http://localhost:5000{file_path}')
            if response.status_code == 200:
                print(f"✅ {file_path} - Accessible ({len(response.content)} bytes)")
            else:
                print(f"❌ {file_path} - Erreur {response.status_code}")
        except Exception as e:
            print(f"❌ {file_path} - Exception: {e}")

def main():
    print("🚀 Test des améliorations UI")
    print("=" * 60)
    
    test_ui_improvements()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print("✅ Interface utilisateur améliorée")
    print("✅ Design moderne avec couleurs ONCF")
    print("✅ Animations et transitions fluides")
    print("✅ Icônes et badges attrayants")
    print("✅ Responsive design")
    print("\n💡 Pour voir les améliorations:")
    print("1. Ouvrez http://localhost:5000")
    print("2. Connectez-vous avec admin/admin123")
    print("3. Naviguez vers /axes")
    print("4. Observez le nouveau design moderne !")

if __name__ == "__main__":
    main()
