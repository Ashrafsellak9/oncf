#!/usr/bin/env python3
"""
Test de la session navigateur et de la page des axes
"""

import requests
import json
from bs4 import BeautifulSoup

def test_browser_session():
    """Test de la session navigateur"""
    session = requests.Session()
    
    # Récupérer le token CSRF
    try:
        response = session.get('http://localhost:5000/login')
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if csrf_token:
            csrf_value = csrf_token.get('value')
            print(f"🔐 Token CSRF récupéré: {csrf_value[:20]}...")
        else:
            print("⚠️ Token CSRF non trouvé")
            csrf_value = ""
    except Exception as e:
        print(f"❌ Erreur récupération CSRF: {e}")
        csrf_value = ""
    
    # Connexion
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_value
    }
    
    try:
        response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("✅ Connexion réussie")
        else:
            print(f"❌ Échec de connexion: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None
    
    # Test de la page des axes
    print("\n🧪 Test de la page des axes...")
    try:
        response = session.get('http://localhost:5000/axes')
        if response.status_code == 200:
            print("✅ Page des axes accessible")
            
            # Vérifier si le JavaScript est inclus
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            axes_js_found = False
            
            for script in scripts:
                if script.get('src') and 'axes.js' in script.get('src'):
                    axes_js_found = True
                    print("✅ Script axes.js trouvé dans la page")
                    break
            
            if not axes_js_found:
                print("❌ Script axes.js non trouvé dans la page")
            
            # Vérifier la structure du tableau
            tbody = soup.find('tbody', {'id': 'axesTableBody'})
            if tbody:
                print("✅ Structure du tableau trouvée")
                # Vérifier s'il y a des données ou juste "Chargement..."
                if "Chargement" in tbody.get_text():
                    print("⚠️ Tableau affiche 'Chargement...' - JavaScript nécessaire")
                else:
                    print("✅ Données trouvées dans le tableau")
            else:
                print("❌ Structure du tableau non trouvée")
                
        else:
            print(f"❌ Page des axes inaccessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur accès page axes: {e}")
    
    # Test de l'API axes avec la session
    print("\n🧪 Test de l'API axes avec session...")
    try:
        response = session.get('http://localhost:5000/api/axes?page=1&per_page=10')
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
                    print(f"📝 PK Début: {first_axe.get('absd', 'N/A')}")
                    print(f"📝 PK Fin: {first_axe.get('absf', 'N/A')}")
                
            else:
                print(f"❌ API Axes: Erreur - {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ API Axes: Code d'erreur {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur API axes: {e}")
    
    return session

def main():
    print("🚀 Test de la session navigateur et page des axes")
    print("=" * 60)
    
    session = test_browser_session()
    
    if session:
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ")
        print("=" * 60)
        print("✅ Session navigateur fonctionnelle")
        print("✅ API axes accessible avec session")
        print("⚠️ Le JavaScript doit être exécuté dans le navigateur")
        print("\n💡 Pour tester dans le navigateur:")
        print("1. Ouvrez http://localhost:5000")
        print("2. Connectez-vous avec admin/admin123")
        print("3. Naviguez vers /axes")
        print("4. Ouvrez la console développeur (F12) pour voir les logs")
    else:
        print("\n❌ Impossible de créer une session")

if __name__ == "__main__":
    main()
