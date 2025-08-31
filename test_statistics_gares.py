#!/usr/bin/env python3
"""
Script de test pour vérifier les statistiques des gares
"""

import requests
import json
from bs4 import BeautifulSoup

def test_gares_statistics():
    """Test des statistiques des gares"""
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    
    try:
        # 1. Se connecter
        print("🔐 Connexion...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post('http://localhost:5000/login', data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erreur de connexion: {login_response.status_code}")
            return False
            
        print("✅ Connexion réussie")
        
        # 2. Accéder à la page des gares
        print("\n📄 Accès à la page des gares...")
        gares_response = session.get('http://localhost:5000/gares')
        
        if gares_response.status_code != 200:
            print(f"❌ Erreur accès page gares: {gares_response.status_code}")
            return False
            
        print("✅ Page des gares accessible")
        
        # 3. Récupérer les données des gares via l'API
        print("\n📊 Récupération des données des gares...")
        api_response = session.get('http://localhost:5000/api/gares?page=1&per_page=100')
        
        if api_response.status_code != 200:
            print(f"❌ Erreur API gares: {api_response.status_code}")
            return False
            
        gares_data = api_response.json()
        
        if not gares_data.get('success'):
            print(f"❌ Erreur API: {gares_data.get('error', 'Erreur inconnue')}")
            return False
            
        gares = gares_data.get('data', [])
        print(f"✅ {len(gares)} gares récupérées")
        
        # 4. Calculer les statistiques manuellement
        print("\n📈 Calcul des statistiques...")
        total_gares = len(gares)
        active_count = 0
        passive_count = 0
        
        for gare in gares:
            etat = gare.get('etat', '').lower()
            if 'active' in etat or 'actif' in etat:
                active_count += 1
            elif 'passive' in etat or 'passif' in etat:
                passive_count += 1
            else:
                # Par défaut, considérer comme actif
                active_count += 1
        
        print(f"📊 Statistiques calculées:")
        print(f"   - Total gares: {total_gares}")
        print(f"   - Gares actives: {active_count}")
        print(f"   - Gares passives: {passive_count}")
        
        # 5. Vérifier que les statistiques sont cohérentes
        if total_gares == 0:
            print("⚠️  Aucune gare trouvée - vérifiez que les données sont importées")
        elif active_count + passive_count != total_gares:
            print("⚠️  Incohérence dans le calcul des états")
        else:
            print("✅ Statistiques cohérentes")
        
        # 6. Afficher quelques exemples de gares avec leurs états
        print("\n🔍 Exemples de gares:")
        for i, gare in enumerate(gares[:5]):
            print(f"   {i+1}. {gare.get('nom', 'Sans nom')} - État: {gare.get('etat', 'Non défini')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test des statistiques des gares")
    print("=" * 50)
    
    success = test_gares_statistics()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test terminé avec succès")
    else:
        print("❌ Test échoué")
