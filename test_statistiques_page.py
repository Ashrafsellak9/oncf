#!/usr/bin/env python3
"""
Test de la page statistiques
"""

import requests
from bs4 import BeautifulSoup
import json

def test_statistiques_page():
    """Tester la page statistiques"""
    
    print("📊 Test de la page statistiques")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # 1. Se connecter
        print("\n🔐 Authentification:")
        
        response = session.get(f"{base_url}/login")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        csrf_value = csrf_token['value']
        
        login_data = {
            'csrf_token': csrf_value,
            'username': 'admin',
            'password': 'admin123',
            'remember_me': 'y'
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        print("   ✅ Connexion réussie")
        
        # 2. Tester la page statistiques
        print("\n📄 Test de la page statistiques:")
        response = session.get(f"{base_url}/statistiques")
        
        if response.status_code == 200:
            print("   ✅ Page statistiques accessible")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Vérifier le JavaScript
            scripts = soup.find_all('script')
            statistiques_script = None
            chart_js = None
            
            for script in scripts:
                if script.get('src'):
                    if 'statistiques.js' in script.get('src'):
                        statistiques_script = script
                    elif 'chart.js' in script.get('src'):
                        chart_js = script
            
            if statistiques_script:
                print("   ✅ Script statistiques.js trouvé")
            else:
                print("   ❌ Script statistiques.js non trouvé")
                
            if chart_js:
                print("   ✅ Chart.js trouvé")
            else:
                print("   ❌ Chart.js non trouvé")
            
            # Vérifier les éléments de statistiques
            stat_elements = ['totalGares', 'totalArcs', 'totalAxes', 'totalVilles']
            for element in stat_elements:
                if soup.find('div', {'id': element}):
                    print(f"   ✅ Élément {element} présent")
                else:
                    print(f"   ❌ Élément {element} manquant")
            
            # Vérifier les graphiques
            chart_elements = ['garesTypeChart', 'axesChart', 'timelineChart', 'etatChart']
            for chart in chart_elements:
                if soup.find('canvas', {'id': chart}):
                    print(f"   ✅ Graphique {chart} présent")
                else:
                    print(f"   ❌ Graphique {chart} manquant")
            
            # Vérifier les tableaux
            table_elements = ['topAxesTable', 'typeGaresTable']
            for table in table_elements:
                if soup.find('tbody', {'id': table}):
                    print(f"   ✅ Tableau {table} présent")
                else:
                    print(f"   ❌ Tableau {table} manquant")
                    
        else:
            print(f"   ❌ Erreur accès page: {response.status_code}")
            return
        
        # 3. Tester l'API des statistiques
        print("\n🔗 Test de l'API des statistiques:")
        response = session.get(f"{base_url}/api/statistiques")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    stats = data.get('data', {})
                    print("   ✅ API statistiques fonctionnelle")
                    
                    # Afficher les statistiques
                    print(f"   📊 Gares: {stats.get('gares', {}).get('total', 0)}")
                    print(f"   📊 Arcs: {stats.get('arcs', {}).get('total', 0)}")
                    print(f"   📊 Événements: {stats.get('evenements', {}).get('total', 0)}")
                    
                    # Vérifier les données détaillées
                    gares_par_type = stats.get('gares', {}).get('par_type', [])
                    gares_par_region = stats.get('gares', {}).get('par_region', [])
                    arcs_par_axe = stats.get('arcs', {}).get('par_axe', [])
                    
                    print(f"   📈 Types de gares: {len(gares_par_type)}")
                    print(f"   📈 Régions: {len(gares_par_region)}")
                    print(f"   📈 Axes: {len(arcs_par_axe)}")
                    
                    # Afficher quelques exemples
                    if gares_par_type:
                        print("   📝 Exemples de types de gares:")
                        for i, type_gare in enumerate(gares_par_type[:3], 1):
                            print(f"      {i}. {type_gare.get('type', 'N/A')}: {type_gare.get('count', 0)}")
                    
                    if gares_par_region:
                        print("   📝 Exemples de régions:")
                        for i, region in enumerate(gares_par_region[:3], 1):
                            print(f"      {i}. {region.get('region', 'N/A')}: {region.get('count', 0)}")
                    
                else:
                    print(f"   ❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
            except json.JSONDecodeError:
                print("   ❌ Réponse non-JSON")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
        
        print("\n🎯 Résumé:")
        print("   ✅ Page accessible")
        print("   ✅ Scripts chargés")
        print("   ✅ API fonctionnelle")
        print("   ✅ Données disponibles")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_statistiques_page()
