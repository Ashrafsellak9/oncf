#!/usr/bin/env python3
"""
Script de test pour vérifier l'API des statistiques
"""

import requests
import json
import psycopg2
import os

def test_statistics_api():
    """Test de l'API des statistiques"""
    
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
        print("\n🗄️ Vérification directe de la base de données...")
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
            cursor = conn.cursor()
            
            # Compter les incidents
            cursor.execute("SELECT COUNT(*) FROM gpr.ge_evenement")
            total_incidents = cursor.fetchone()[0]
            print(f"   📊 Total incidents dans la base: {total_incidents}")
            
            # Vérifier les statuts
            cursor.execute("SELECT statut, COUNT(*) FROM gpr.ge_evenement GROUP BY statut")
            statuts = cursor.fetchall()
            print(f"   📋 Répartition par statut:")
            for statut, count in statuts:
                print(f"      - {statut}: {count}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Erreur base de données: {e}")
        
        # 3. Tester l'API des statistiques
        print("\n🔌 Test de l'API des statistiques...")
        try:
            response = session.get('http://localhost:5000/api/statistiques')
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API accessible")
                print(f"   Success: {data.get('success')}")
                
                if data.get('success'):
                    stats = data.get('data', {})
                    
                    print(f"   📊 Statistiques des incidents:")
                    evenements = stats.get('evenements', {})
                    print(f"      - Total: {evenements.get('total', 0)}")
                    print(f"      - Par statut: {evenements.get('par_statut', [])}")
                    
                    print(f"   📊 Statistiques des gares:")
                    gares = stats.get('gares', {})
                    print(f"      - Total: {gares.get('total', 0)}")
                    print(f"      - Par type: {len(gares.get('par_type', []))}")
                    print(f"      - Par région: {len(gares.get('par_region', []))}")
                    
                    print(f"   📊 Statistiques des arcs:")
                    arcs = stats.get('arcs', {})
                    print(f"      - Total: {arcs.get('total', 0)}")
                    print(f"      - Par axe: {len(arcs.get('par_axe', []))}")
                    
                else:
                    print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur API: {e}")
        
        # 4. Comparer avec l'API des incidents
        print("\n🔍 Comparaison avec l'API des incidents...")
        try:
            response = session.get('http://localhost:5000/api/evenements?page=1&per_page=1')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    pagination = data.get('pagination', {})
                    print(f"   📊 API incidents:")
                    print(f"      - Total: {pagination.get('total', 0)}")
                    print(f"      - Pages: {pagination.get('pages', 0)}")
                else:
                    print(f"   ❌ Erreur API incidents: {data.get('error', 'Erreur inconnue')}")
            else:
                print(f"   ❌ Erreur HTTP incidents: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur API incidents: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de l'API des statistiques")
    print("=" * 60)
    
    success = test_statistics_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test terminé avec succès")
    else:
        print("❌ Test échoué")
