#!/usr/bin/env python3
"""
Script pour vérifier le mapping des données dans la table ge_evenement
"""

import psycopg2
import os

def check_incidents_mapping():
    """Vérifier le mapping des données dans la table ge_evenement"""
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        print("🔍 Vérification du mapping des données dans ge_evenement")
        print("=" * 80)
        
        # 1. Vérifier la structure de la table
        print("\n📋 Structure de la table ge_evenement:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'ge_evenement' 
            AND table_schema = 'gpr' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # 2. Vérifier quelques exemples de données
        print("\n📊 Exemples de données actuelles:")
        cursor.execute("""
            SELECT id, date_debut, date_fin, heure_debut, heure_fin, 
                   resume, description, axe, section, gare, 
                   type_id, sous_type_id, source_id, statut
            FROM gpr.ge_evenement 
            LIMIT 5
        """)
        
        incidents = cursor.fetchall()
        for i, incident in enumerate(incidents):
            print(f"\n   Incident {i+1}:")
            print(f"      ID: {incident[0]}")
            print(f"      Date début: {incident[1]}")
            print(f"      Date fin: {incident[2]}")
            print(f"      Heure début: {incident[3]}")
            print(f"      Heure fin: {incident[4]}")
            print(f"      Résumé: {incident[5]}")
            print(f"      Description: {incident[6]}")
            print(f"      Axe: {incident[7]}")
            print(f"      Section: {incident[8]}")
            print(f"      Gare: {incident[9]}")
            print(f"      Type ID: {incident[10]}")
            print(f"      Sous-type ID: {incident[11]}")
            print(f"      Source ID: {incident[12]}")
            print(f"      Statut: {incident[13]}")
        
        # 3. Vérifier les valeurs uniques pour certains champs
        print("\n📈 Analyse des valeurs:")
        
        # Statuts
        cursor.execute("SELECT statut, COUNT(*) FROM gpr.ge_evenement GROUP BY statut")
        statuts = cursor.fetchall()
        print(f"   Statuts: {statuts}")
        
        # Types
        cursor.execute("SELECT type_id, COUNT(*) FROM gpr.ge_evenement GROUP BY type_id")
        types = cursor.fetchall()
        print(f"   Types: {types}")
        
        # Axes
        cursor.execute("SELECT axe, COUNT(*) FROM gpr.ge_evenement WHERE axe IS NOT NULL GROUP BY axe LIMIT 10")
        axes = cursor.fetchall()
        print(f"   Axes (top 10): {axes}")
        
        # Sections
        cursor.execute("SELECT section, COUNT(*) FROM gpr.ge_evenement WHERE section IS NOT NULL GROUP BY section LIMIT 10")
        sections = cursor.fetchall()
        print(f"   Sections (top 10): {sections}")
        
        # 4. Vérifier les relations
        print("\n🔗 Vérification des relations:")
        
        # Vérifier si les type_id existent dans ref_types
        cursor.execute("""
            SELECT COUNT(*) FROM gpr.ge_evenement e 
            LEFT JOIN gpr.ref_types t ON e.type_id = t.id 
            WHERE e.type_id IS NOT NULL AND t.id IS NULL
        """)
        invalid_types = cursor.fetchone()[0]
        print(f"   Type IDs invalides: {invalid_types}")
        
        # Vérifier si les source_id existent dans ref_sources
        cursor.execute("""
            SELECT COUNT(*) FROM gpr.ge_evenement e 
            LEFT JOIN gpr.ref_sources s ON e.source_id = s.id 
            WHERE e.source_id IS NOT NULL AND s.id IS NULL
        """)
        invalid_sources = cursor.fetchone()[0]
        print(f"   Source IDs invalides: {invalid_sources}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_incidents_mapping()
