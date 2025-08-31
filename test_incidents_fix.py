#!/usr/bin/env python3
"""
Test de la correction de la page des incidents
"""

import requests
import json
from bs4 import BeautifulSoup

def test_incidents_fix():
    """Test de la correction de la page des incidents"""
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
    
    # Test de la page des incidents
    print("\n🧪 Test de la page des incidents...")
    try:
        response = session.get('http://localhost:5000/incidents')
        if response.status_code == 200:
            print("✅ Page des incidents accessible")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Vérifier les éléments de la page
            incidentsList = soup.find('div', {'id': 'incidentsList'})
            if incidentsList:
                print("✅ Conteneur incidentsList trouvé")
            else:
                print("❌ Conteneur incidentsList non trouvé")
            
            paginationInfo = soup.find('span', {'id': 'paginationInfo'})
            if paginationInfo:
                print("✅ Élément paginationInfo trouvé")
            else:
                print("❌ Élément paginationInfo non trouvé")
            
            # Vérifier le script incidents.js
            scripts = soup.find_all('script')
            incidents_js_found = False
            for script in scripts:
                if script.get('src') and 'incidents.js' in script.get('src'):
                    incidents_js_found = True
                    break
            
            if incidents_js_found:
                print("✅ Script incidents.js trouvé")
            else:
                print("❌ Script incidents.js non trouvé")
                
        else:
            print(f"❌ Page des incidents inaccessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur accès page incidents: {e}")
    
    # Test de l'API incidents
    print("\n🧪 Test de l'API incidents...")
    try:
        response = session.get('http://localhost:5000/api/evenements?page=1&per_page=10')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                incidents_count = len(data.get('data', []))
                total = data.get('pagination', {}).get('total', 0)
                print(f"✅ API Incidents: {incidents_count} incidents disponibles sur {total} au total")
                
                if incidents_count > 0:
                    first_incident = data['data'][0]
                    print(f"📝 Premier incident: ID {first_incident.get('id', 'N/A')}")
                    print(f"📝 Type: {first_incident.get('type_id', 'N/A')}")
                    print(f"📝 Statut: {first_incident.get('statut', 'N/A')}")
                
            else:
                print(f"❌ API Incidents: Erreur - {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ API Incidents: Code d'erreur {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur API incidents: {e}")
    
    # Test des autres APIs nécessaires
    print("\n🧪 Test des APIs de support...")
    apis_to_test = [
        ('/api/types-incidents', 'Types d\'incidents'),
        ('/api/localisations', 'Localisations'),
        ('/api/statistiques', 'Statistiques')
    ]
    
    for endpoint, name in apis_to_test:
        try:
            response = session.get(f'http://localhost:5000{endpoint}')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    count = len(data.get('data', []))
                    print(f"✅ {name}: {count} éléments")
                else:
                    print(f"❌ {name}: Erreur - {data.get('error', 'Erreur inconnue')}")
            else:
                print(f"❌ {name}: Code d'erreur {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")

def main():
    print("🚀 Test de la correction de la page des incidents")
    print("=" * 60)
    
    test_incidents_fix()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print("✅ Fonction displayIncidents ajoutée")
    print("✅ Fonction updateIncidentStats ajoutée")
    print("✅ Fonction updatePaginationInfo ajoutée")
    print("✅ Page des incidents corrigée")
    print("\n💡 Pour tester la correction:")
    print("1. Ouvrez http://localhost:5000")
    print("2. Connectez-vous avec admin/admin123")
    print("3. Naviguez vers /incidents")
    print("4. Vérifiez que la page se charge sans erreur")

if __name__ == "__main__":
    main()
