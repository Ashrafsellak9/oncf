#!/usr/bin/env python3
"""
Test détaillé de la connexion pour comprendre le problème d'authentification
"""

import requests
from bs4 import BeautifulSoup

def test_login_detailed():
    """Test détaillé de la connexion"""
    
    print("🔐 Test détaillé de la connexion")
    print("=" * 40)
    
    session = requests.Session()
    
    try:
        # 1. Accéder à la page de connexion
        print("\n1️⃣ Accès à la page de connexion...")
        login_page = session.get('http://localhost:5000/login')
        print(f"Status: {login_page.status_code}")
        
        # 2. Extraire le CSRF token
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if csrf_token:
            csrf_value = csrf_token.get('value')
            print(f"CSRF token trouvé: {csrf_value[:20]}...")
        else:
            print("❌ CSRF token non trouvé")
            return False
        
        # 3. Tentative de connexion avec CSRF token
        print("\n2️⃣ Tentative de connexion...")
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_value
        }
        
        login_response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        print(f"Status de connexion: {login_response.status_code}")
        print(f"Headers de réponse: {dict(login_response.headers)}")
        
        # 4. Vérifier les cookies
        print(f"\n3️⃣ Cookies après connexion:")
        for cookie in session.cookies:
            print(f"  {cookie.name}: {cookie.value[:50]}...")
        
        # 5. Tester l'accès à une page protégée
        print("\n4️⃣ Test d'accès à une page protégée...")
        dashboard_response = session.get('http://localhost:5000/dashboard', allow_redirects=False)
        print(f"Status dashboard: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 302:
            print(f"Redirection vers: {dashboard_response.headers.get('Location', 'Inconnu')}")
        
        # 6. Tester l'accès aux statistiques
        print("\n5️⃣ Test d'accès aux statistiques...")
        stats_response = session.get('http://localhost:5000/statistiques', allow_redirects=False)
        print(f"Status statistiques: {stats_response.status_code}")
        
        if stats_response.status_code == 302:
            print(f"Redirection vers: {stats_response.headers.get('Location', 'Inconnu')}")
        elif stats_response.status_code == 200:
            # Vérifier le contenu
            soup = BeautifulSoup(stats_response.text, 'html.parser')
            title = soup.find('title')
            print(f"Titre de la page: {title.text if title else 'Non trouvé'}")
            
            if 'statistiques.js' in stats_response.text:
                print("✅ statistiques.js trouvé dans la page")
            else:
                print("❌ statistiques.js non trouvé dans la page")
        
        # 7. Vérifier la session
        print("\n6️⃣ Vérification de la session...")
        session_response = session.get('http://localhost:5000/api/profile')
        print(f"Status API profile: {session_response.status_code}")
        
        if session_response.status_code == 200:
            try:
                data = session_response.json()
                if data.get('success'):
                    print("✅ Session valide - utilisateur connecté")
                    print(f"  Utilisateur: {data['data']['username']}")
                else:
                    print("❌ Session invalide")
            except:
                print("❌ Réponse API invalide")
        else:
            print("❌ Impossible d'accéder à l'API profile")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_detailed()
