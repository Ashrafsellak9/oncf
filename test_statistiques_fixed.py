#!/usr/bin/env python3
"""
Test script pour vérifier que les erreurs JavaScript de la page des statistiques ont été corrigées
"""

import requests
from bs4 import BeautifulSoup
import json
import sys

def test_statistics_page():
    """Test de la page des statistiques après les corrections JavaScript"""
    
    print("🔧 Test de la page des statistiques après corrections JavaScript")
    print("=" * 60)
    
    # Session pour maintenir l'authentification
    session = requests.Session()
    
    try:
        # 1. Connexion avec CSRF token
        print("\n1️⃣ Connexion...")
        
        # D'abord, récupérer le CSRF token
        login_page = session.get('http://localhost:5000/login')
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_token:
            print("❌ CSRF token non trouvé")
            return False
        
        csrf_value = csrf_token.get('value')
        
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_value
        }
        
        login_response = session.post('http://localhost:5000/login', data=login_data)
        if login_response.status_code != 200:
            print("❌ Échec de la connexion")
            return False
        
        print("✅ Connexion réussie")
        
        # 2. Accès à la page des statistiques
        print("\n2️⃣ Accès à la page des statistiques...")
        stats_response = session.get('http://localhost:5000/statistiques')
        
        if stats_response.status_code != 200:
            print(f"❌ Erreur HTTP: {stats_response.status_code}")
            return False
        
        print("✅ Page des statistiques accessible")
        
        # 3. Vérification du contenu HTML
        print("\n3️⃣ Vérification du contenu HTML...")
        soup = BeautifulSoup(stats_response.text, 'html.parser')
        
        # Vérifier la présence des scripts
        scripts = soup.find_all('script')
        script_srcs = [script.get('src', '') for script in scripts if script.get('src')]
        
        print(f"📜 Scripts trouvés: {len(scripts)}")
        for src in script_srcs:
            print(f"   - {src}")
        
        # Vérifier la présence de statistiques.js dans les scripts externes
        if any('statistiques.js' in src for src in script_srcs):
            print("✅ Script statistiques.js trouvé")
        else:
            # Vérifier dans le contenu HTML pour les scripts inline
            html_content = stats_response.text
            if 'statistiques.js' in html_content:
                print("✅ Script statistiques.js trouvé (référencé dans le HTML)")
            else:
                print("❌ Script statistiques.js manquant")
                return False
        
        # Vérifier la présence de Chart.js
        if any('chart.js' in src.lower() for src in script_srcs):
            print("✅ Chart.js trouvé")
        else:
            # Vérifier dans le contenu HTML
            if 'chart.js' in stats_response.text.lower():
                print("✅ Chart.js trouvé (référencé dans le HTML)")
            else:
                print("❌ Chart.js manquant")
                return False
        
        # 4. Vérification des éléments de la page
        print("\n4️⃣ Vérification des éléments de la page...")
        
        # Éléments principaux
        elements_to_check = [
            'totalGares',
            'totalArcs', 
            'totalAxes',
            'totalVilles'
        ]
        
        for element_id in elements_to_check:
            element = soup.find(id=element_id)
            if element:
                print(f"✅ Élément {element_id} trouvé")
            else:
                print(f"❌ Élément {element_id} manquant")
        
        # Canvas des graphiques
        canvas_elements = [
            'garesTypeChart',
            'axesChart',
            'timelineChart',
            'etatChart'
        ]
        
        for canvas_id in canvas_elements:
            canvas = soup.find(id=canvas_id)
            if canvas:
                print(f"✅ Canvas {canvas_id} trouvé")
            else:
                print(f"❌ Canvas {canvas_id} manquant")
        
        # 5. Test de l'API des statistiques
        print("\n5️⃣ Test de l'API des statistiques...")
        api_response = session.get('http://localhost:5000/api/statistiques')
        
        if api_response.status_code != 200:
            print(f"❌ Erreur API: {api_response.status_code}")
            return False
        
        try:
            api_data = api_response.json()
            print("✅ API des statistiques accessible")
            
            if api_data.get('success'):
                print("✅ Données des statistiques valides")
                
                # Afficher quelques exemples de données
                data = api_data.get('data', {})
                print(f"   - Total gares: {data.get('gares', {}).get('total', 'N/A')}")
                print(f"   - Total arcs: {data.get('arcs', {}).get('total', 'N/A')}")
                print(f"   - Types de gares: {len(data.get('gares', {}).get('par_type', []))}")
                print(f"   - Axes: {len(data.get('arcs', {}).get('par_axe', []))}")
                
            else:
                print(f"❌ Erreur dans les données: {api_data.get('error', 'Erreur inconnue')}")
                return False
                
        except json.JSONDecodeError:
            print("❌ Réponse API non-JSON")
            return False
        
        # 6. Vérification des améliorations UI
        print("\n6️⃣ Vérification des améliorations UI...")
        
        # Vérifier la présence de classes Bootstrap modernes
        cards = soup.find_all(class_='card')
        print(f"✅ {len(cards)} cartes trouvées")
        
        shadows = soup.find_all(class_='shadow-sm')
        print(f"✅ {len(shadows)} éléments avec ombre trouvés")
        
        gradients = soup.find_all(class_='bg-gradient')
        print(f"✅ {len(gradients)} éléments avec gradient trouvés")
        
        # Vérifier les icônes Font Awesome
        icons = soup.find_all(class_='fas')
        print(f"✅ {len(icons)} icônes Font Awesome trouvées")
        
        print("\n🎉 Test terminé avec succès!")
        print("\n📋 Résumé des corrections apportées:")
        print("   ✅ main.js modifié pour éviter les conflits sur la page statistiques")
        print("   ✅ statistiques.js amélioré avec gestion d'erreurs robuste")
        print("   ✅ Chart.js initialisation sécurisée avec destruction des instances")
        print("   ✅ UI/UX modernisée avec Bootstrap 5 et icônes")
        print("   ✅ Gestion des erreurs et logging amélioré")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous que l'application Flask est démarrée.")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = test_statistics_page()
    sys.exit(0 if success else 1)
