#!/usr/bin/env python3
"""
Script de test pour vérifier les nouvelles statistiques des gares
"""

import requests
import json
from bs4 import BeautifulSoup

def test_gares_stats_fix():
    """Test des nouvelles statistiques des gares"""
    
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
        
        # 2. Tester la nouvelle API de statistiques
        print("\n📊 Test de l'API /api/gares/stats...")
        stats_response = session.get('http://localhost:5000/api/gares/stats')
        
        if stats_response.status_code != 200:
            print(f"❌ Erreur API stats: {stats_response.status_code}")
            return False
            
        stats_data = stats_response.json()
        
        if not stats_data.get('success'):
            print(f"❌ Erreur API stats: {stats_data.get('error', 'Erreur inconnue')}")
            return False
            
        stats = stats_data.get('data', {})
        total_gares = stats.get('total_gares', 0)
        active_gares = stats.get('active_gares', 0)
        passive_gares = stats.get('passive_gares', 0)
        
        print(f"✅ Statistiques globales récupérées:")
        print(f"   - Total gares: {total_gares}")
        print(f"   - Gares actives: {active_gares}")
        print(f"   - Gares passives: {passive_gares}")
        
        # 3. Comparer avec les données paginées
        print("\n📄 Comparaison avec les données paginées...")
        api_response = session.get('http://localhost:5000/api/gares?page=1&per_page=25')
        
        if api_response.status_code != 200:
            print(f"❌ Erreur API gares: {api_response.status_code}")
            return False
            
        gares_data = api_response.json()
        
        if not gares_data.get('success'):
            print(f"❌ Erreur API gares: {gares_data.get('error', 'Erreur inconnue')}")
            return False
            
        gares_page = gares_data.get('data', [])
        pagination = gares_data.get('pagination', {})
        total_pagination = pagination.get('total', 0)
        
        print(f"✅ Données paginées:")
        print(f"   - Gares sur cette page: {len(gares_page)}")
        print(f"   - Total selon pagination: {total_pagination}")
        
        # 4. Vérifier la cohérence
        if total_gares == total_pagination:
            print("✅ Les totaux sont cohérents")
        else:
            print(f"⚠️  Incohérence: Total stats={total_gares}, Total pagination={total_pagination}")
        
        # 5. Tester avec tous les filtres
        print("\n🔍 Test des filtres...")
        filters_response = session.get('http://localhost:5000/api/gares/filters')
        
        if filters_response.status_code == 200:
            filters_data = filters_response.json()
            if filters_data.get('success'):
                filters = filters_data.get('data', {})
                print(f"✅ Filtres disponibles:")
                print(f"   - Sections: {len(filters.get('sections', []))}")
                print(f"   - Types: {len(filters.get('types', []))}")
                print(f"   - États: {len(filters.get('etats', []))}")
                print(f"   - Régions: {len(filters.get('regions', []))}")
                print(f"   - Villes: {len(filters.get('villes', []))}")
        
        # 6. Afficher quelques exemples de gares
        print("\n🔍 Exemples de gares:")
        for i, gare in enumerate(gares_page[:3]):
            print(f"   {i+1}. {gare.get('nom', 'Sans nom')} - État: {gare.get('etat', 'Non défini')} - Région: {gare.get('region', 'Non définie')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test des nouvelles statistiques des gares")
    print("=" * 60)
    
    success = test_gares_stats_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test terminé avec succès")
    else:
        print("❌ Test échoué")
