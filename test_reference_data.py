#!/usr/bin/env python3
"""
Test script pour vérifier que les données de référence sont bien liées
"""

import psycopg2
import requests

def test_reference_data():
    """Tester que les données de référence sont bien liées"""
    
    print("🧪 Test des données de référence")
    print("=" * 50)
    
    # Test 1: Vérifier les données dans la base
    print("\n1. Vérification des données dans la base...")
    conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/oncf_achraf')
    cur = conn.cursor()
    
    # Vérifier quelques incidents avec leurs références
    cur.execute("""
        SELECT e.id, e.resume, 
               t.intitule as type_name,
               st.intitule as sous_type_name,
               s.intitule as source_name,
               sys.intitule as system_name,
               ent.intitule as entite_name
        FROM gpr.ge_evenement e
        LEFT JOIN gpr.ref_types t ON e.type_id = t.id
        LEFT JOIN gpr.ref_sous_types st ON e.sous_type_id = st.id
        LEFT JOIN gpr.ref_sources s ON e.source_id = s.id
        LEFT JOIN gpr.ref_systemes sys ON e.system_id = sys.id
        LEFT JOIN gpr.ref_entites ent ON e.entite_id = ent.id
        LIMIT 5
    """)
    
    incidents = cur.fetchall()
    for incident in incidents:
        print(f"\n   Incident {incident[0]}:")
        print(f"      Résumé: {incident[1][:100]}...")
        print(f"      Type: {incident[2]}")
        print(f"      Sous-type: {incident[3]}")
        print(f"      Source: {incident[4]}")
        print(f"      Système: {incident[5]}")
        print(f"      Entité: {incident[6]}")
    
    cur.close()
    conn.close()
    
    # Test 2: Vérifier l'API
    print("\n2. Test de l'API incidents...")
    try:
        response = requests.get('http://localhost:5000/api/evenements?page=1&per_page=3')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API répond correctement")
            print(f"   Total incidents: {data['pagination']['total']}")
            
            for incident in data['data']:
                print(f"\n   Incident {incident['id']}:")
                print(f"      Description: {incident['description'][:100]}...")
                print(f"      Type ID: {incident['type_id']}")
                print(f"      Sous-type ID: {incident['sous_type_id']}")
                print(f"      Source ID: {incident['source_id']}")
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur connexion API: {e}")
    
    # Test 3: Vérifier les détails d'un incident
    print("\n3. Test des détails d'incident...")
    try:
        response = requests.get('http://localhost:5000/api/evenements/348/details')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Détails récupérés")
            
            incident = data['data']
            print(f"\n   Détails incident {incident['id']}:")
            print(f"      Type: {incident['type']}")
            print(f"      Sous-type: {incident['sous_type']}")
            print(f"      Source: {incident['source']}")
            print(f"      Entité: {incident['entite_ref']}")
        else:
            print(f"   ❌ Erreur détails: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur détails: {e}")
    
    print("\n✅ Test terminé!")

if __name__ == "__main__":
    test_reference_data()
