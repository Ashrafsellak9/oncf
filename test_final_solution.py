#!/usr/bin/env python3
"""
Test final de toutes les fonctionnalités
"""

import requests
import json
from datetime import datetime

def create_authenticated_session():
    """Créer une session authentifiée"""
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
    
    # Connexion
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_value
    }
    
    try:
        response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        if response.status_code == 302:  # Redirection après connexion réussie
            print("✅ Connexion réussie")
            return session
        else:
            print(f"❌ Échec de connexion: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_axes_data(session):
    """Test des données des axes"""
    print("\n🧪 Test des données des axes...")
    
    try:
        response = session.get('http://localhost:5000/api/axes?page=1&per_page=10')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                axes_count = len(data.get('data', []))
                total = data.get('pagination', {}).get('total', 0)
                print(f"✅ API Axes: {axes_count} axes affichés sur {total} au total")
                
                if axes_count > 0:
                    first_axe = data['data'][0]
                    print(f"📝 Premier axe: {first_axe.get('axe', 'N/A')}")
                
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

def test_reference_data(session):
    """Test des données de référence"""
    print("\n🧪 Test des données de référence...")
    
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

def test_statistics_data(session):
    """Test des données des statistiques"""
    print("\n🧪 Test des données des statistiques...")
    
    try:
        response = session.get('http://localhost:5000/api/statistiques')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('data', {})
                
                # Vérifier les différentes sections
                sections = ['gares', 'axes', 'evenements', 'types']
                for section in sections:
                    if section in stats:
                        print(f"✅ Statistiques {section}: Données disponibles")
                    else:
                        print(f"⚠️ Statistiques {section}: Pas de données")
                
                return True
            else:
                print(f"❌ API Statistiques: Erreur - {data.get('error', 'Erreur inconnue')}")
                return False
        else:
            print(f"❌ API Statistiques: Code d'erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Statistiques: Exception - {e}")
        return False

def test_public_endpoints():
    """Test des endpoints publics"""
    print("\n🧪 Test des endpoints publics...")
    
    endpoints = [
        ('/api/gares', 'Gares'),
        ('/api/evenements', 'Événements'),
        ('/api/types-incidents', 'Types d\'incidents'),
        ('/api/localisations', 'Localisations')
    ]
    
    success_count = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'http://localhost:5000{endpoint}')
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
    print("🚀 Test final de toutes les fonctionnalités")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Créer une session authentifiée
    session = create_authenticated_session()
    
    if not session:
        print("❌ Impossible de créer une session authentifiée")
        return
    
    # Tests avec authentification
    axes_ok = test_axes_data(session)
    ref_ok = test_reference_data(session)
    stats_ok = test_statistics_data(session)
    
    # Tests sans authentification (endpoints publics)
    public_ok = test_public_endpoints()
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 60)
    print(f"📈 Données des axes: {'✅ OK' if axes_ok else '❌ ÉCHEC'}")
    print(f"📋 Données de référence: {'✅ OK' if ref_ok else '❌ ÉCHEC'}")
    print(f"📊 Données des statistiques: {'✅ OK' if stats_ok else '❌ ÉCHEC'}")
    print(f"🌐 Endpoints publics: {'✅ OK' if public_ok else '❌ ÉCHEC'}")
    
    total_tests = 4
    passed_tests = sum([axes_ok, ref_ok, stats_ok, public_ok])
    
    print(f"\n🎯 Score: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 Toutes les fonctionnalités fonctionnent correctement !")
        print("💡 Les pages axes et statistiques devraient maintenant afficher les données.")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} problème(s) détecté(s).")
        print("Vérifiez les logs de l'application pour plus de détails.")

if __name__ == "__main__":
    main()
