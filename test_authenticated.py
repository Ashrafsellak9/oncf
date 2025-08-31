#!/usr/bin/env python3
"""
Test des endpoints protégés avec authentification
"""

import requests
import json
from datetime import datetime

def login():
    """Se connecter à l'application"""
    session = requests.Session()
    
    # Récupérer le token CSRF
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
    
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_value
    }
    
    try:
        response = session.post('http://localhost:5000/login', data=login_data)
        if response.status_code == 302:  # Redirection après connexion réussie
            print("✅ Connexion réussie")
            return session
        else:
            print(f"❌ Échec de connexion: {response.status_code}")
            print(f"📝 Contenu de réponse: {response.text[:200]}...")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_axes_with_auth():
    """Test des axes avec authentification"""
    print("🧪 Test des axes avec authentification...")
    
    session = login()
    if not session:
        return False
    
    try:
        response = session.get('http://localhost:5000/api/axes?page=1&per_page=10')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                axes_count = len(data.get('data', []))
                total = data.get('pagination', {}).get('total', 0)
                print(f"✅ API Axes: {axes_count} axes affichés sur {total} au total")
                return True
            else:
                print(f"❌ API Axes: Erreur - {data.get('error', 'Erreur inconnue')}")
                return False
        else:
            print(f"❌ API Axes: Code d'erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Axes: Exception - {e}")
        return False

def test_reference_with_auth():
    """Test des données de référence avec authentification"""
    print("🧪 Test des données de référence avec authentification...")
    
    session = login()
    if not session:
        return False
    
    endpoints = [
        ('/api/reference/types', 'Types'),
        ('/api/reference/sous-types', 'Sous-types'),
        ('/api/reference/systemes', 'Systèmes'),
        ('/api/reference/sources', 'Sources'),
        ('/api/reference/entites', 'Entités')
    ]
    
    success_count = 0
    for endpoint, name in endpoints:
        try:
            response = session.get(f'http://localhost:5000{endpoint}')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    count = len(data.get('data', []))
                    print(f"✅ {name}: {count} éléments")
                    success_count += 1
                else:
                    print(f"❌ {name}: Erreur - {data.get('error', 'Erreur inconnue')}")
            else:
                print(f"❌ {name}: Code d'erreur {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")
    
    return success_count == len(endpoints)

def main():
    print("🚀 Test des endpoints protégés avec authentification")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Tests avec authentification
    axes_ok = test_axes_with_auth()
    print()
    
    ref_ok = test_reference_with_auth()
    print()
    
    # Résumé
    print("=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print(f"📈 Données des axes: {'✅ OK' if axes_ok else '❌ ÉCHEC'}")
    print(f"📋 Données de référence: {'✅ OK' if ref_ok else '❌ ÉCHEC'}")
    
    if axes_ok and ref_ok:
        print("\n🎉 Toutes les données sont correctement accessibles !")
        print("💡 Les pages axes et statistiques devraient maintenant afficher les données.")
    else:
        print("\n⚠️ Certaines données ne sont pas accessibles.")
        print("Vérifiez les logs de l'application pour plus de détails.")

if __name__ == "__main__":
    main()
