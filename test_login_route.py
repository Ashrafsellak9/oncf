#!/usr/bin/env python3
"""
Test de la route de connexion
"""

import requests
import json

def test_login_route():
    """Test de la route de connexion"""
    print("🧪 Test de la route de connexion...")
    
    session = requests.Session()
    
    # Test 1: Accéder à la page de connexion
    try:
        response = session.get('http://localhost:5000/login')
        print(f"📄 Page de connexion - Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Page de connexion accessible")
        else:
            print("❌ Page de connexion inaccessible")
            return False
    except Exception as e:
        print(f"❌ Erreur accès page connexion: {e}")
        return False
    
    # Test 2: Récupérer le token CSRF
    try:
        response = session.get('http://localhost:5000/login')
        from bs4 import BeautifulSoup
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
    
    # Test 3: Tentative de connexion
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'remember_me': False,
        'csrf_token': csrf_value
    }
    
    try:
        response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        print(f"🔑 Tentative de connexion - Status: {response.status_code}")
        print(f"📋 Headers de réponse: {dict(response.headers)}")
        
        if response.status_code == 302:  # Redirection après connexion réussie
            location = response.headers.get('Location', '')
            print(f"🔄 Redirection vers: {location}")
            
            if location == '/':
                print("✅ Connexion réussie - Redirection vers le dashboard")
                return session
            else:
                print(f"⚠️ Redirection inattendue: {location}")
                return session
        else:
            print("❌ Connexion échouée")
            print(f"📝 Contenu de réponse: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None

def test_protected_route(session):
    """Test d'une route protégée après connexion"""
    if not session:
        print("❌ Pas de session disponible")
        return False
    
    print("\n🧪 Test d'une route protégée...")
    
    try:
        response = session.get('http://localhost:5000/api/axes?page=1&per_page=5')
        print(f"📊 API Axes - Status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'Non spécifié')}")
        
        if response.status_code == 200:
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    print("✅ Réponse JSON reçue")
                    print(f"📝 Données: {json.dumps(data, indent=2)[:200]}...")
                    return True
                except json.JSONDecodeError:
                    print("❌ Réponse non-JSON")
                    print(f"📝 Contenu: {response.text[:200]}...")
                    return False
            else:
                print("❌ Réponse non-JSON")
                print(f"📝 Contenu: {response.text[:200]}...")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    print("🚀 Test de la route de connexion")
    print("=" * 50)
    
    # Test de connexion
    session = test_login_route()
    
    if session:
        # Test d'une route protégée
        success = test_protected_route(session)
        
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ")
        print("=" * 50)
        if success:
            print("🎉 Connexion et accès aux routes protégées réussis !")
        else:
            print("⚠️ Connexion réussie mais problème avec les routes protégées")
    else:
        print("\n❌ Échec de la connexion")

if __name__ == "__main__":
    main()
