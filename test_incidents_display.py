#!/usr/bin/env python3
"""
Script de test pour vérifier l'affichage des incidents
"""

import requests
import json
import psycopg2
import os
from bs4 import BeautifulSoup

def test_incidents_display():
    """Test de l'affichage des incidents"""
    
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
        
        # 2. Vérifier la base de données directement
        print("\n🗄️ Vérification de la base de données...")
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
            cursor = conn.cursor()
            
            # Compter les incidents
            cursor.execute("SELECT COUNT(*) FROM gpr.ge_evenement")
            total_incidents = cursor.fetchone()[0]
            print(f"   📊 Total incidents dans la base: {total_incidents}")
            
            # Vérifier quelques incidents
            cursor.execute("SELECT id, statut, description FROM gpr.ge_evenement LIMIT 5")
            incidents = cursor.fetchall()
            print(f"   📋 Exemples d'incidents:")
            for incident in incidents:
                print(f"      - ID: {incident[0]}, Statut: {incident[1]}, Description: {incident[2][:50]}...")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Erreur base de données: {e}")
        
        # 3. Tester l'API des incidents
        print("\n🔌 Test de l'API des incidents...")
        try:
            response = session.get('http://localhost:5000/api/evenements?page=1&per_page=10')
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API accessible")
                print(f"   Success: {data.get('success')}")
                
                if data.get('success'):
                    pagination = data.get('pagination', {})
                    incidents_data = data.get('data', [])
                    
                    print(f"   📊 Pagination:")
                    print(f"      - Total: {pagination.get('total', 0)}")
                    print(f"      - Pages: {pagination.get('pages', 0)}")
                    print(f"      - Page actuelle: {pagination.get('page', 0)}")
                    print(f"      - Par page: {pagination.get('per_page', 0)}")
                    
                    print(f"   📋 Incidents retournés: {len(incidents_data)}")
                    
                    if incidents_data:
                        print(f"   🔍 Premier incident:")
                        first_incident = incidents_data[0]
                        print(f"      - ID: {first_incident.get('id')}")
                        print(f"      - Statut: {first_incident.get('statut')}")
                        print(f"      - Description: {first_incident.get('description', '')[:50]}...")
                else:
                    print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur API: {e}")
        
        # 4. Tester la page des incidents
        print("\n🌐 Test de la page des incidents...")
        try:
            response = session.get('http://localhost:5000/incidents')
            
            if response.status_code == 200:
                print("✅ Page des incidents accessible")
                
                # Vérifier si la page contient des éléments d'interface
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Vérifier les éléments d'interface
                incidents_list = soup.find('div', {'id': 'incidentsList'})
                if incidents_list:
                    print("   ✅ Container des incidents trouvé")
                else:
                    print("   ❌ Container des incidents non trouvé")
                
                # Vérifier les filtres
                status_filter = soup.find('select', {'id': 'statusFilter'})
                if status_filter:
                    print("   ✅ Filtre de statut trouvé")
                else:
                    print("   ❌ Filtre de statut non trouvé")
                
                # Vérifier les statistiques
                stats_elements = soup.find_all('div', class_='stat-card')
                print(f"   📊 Cartes de statistiques trouvées: {len(stats_elements)}")
                
            else:
                print(f"❌ Erreur page incidents: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur page incidents: {e}")
        
        # 5. Tester les statistiques
        print("\n📊 Test des statistiques...")
        try:
            response = session.get('http://localhost:5000/api/statistiques')
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API statistiques accessible")
                
                if data.get('success'):
                    stats = data.get('data', {})
                    print(f"   📈 Statistiques:")
                    print(f"      - Total incidents: {stats.get('total_evenements', 0)}")
                    print(f"      - Incidents par statut: {stats.get('evenements_par_statut', [])}")
                else:
                    print(f"❌ Erreur statistiques: {data.get('error', 'Erreur inconnue')}")
            else:
                print(f"❌ Erreur HTTP statistiques: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur statistiques: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de l'affichage des incidents")
    print("=" * 60)
    
    success = test_incidents_display()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test terminé avec succès")
    else:
        print("❌ Test échoué")
