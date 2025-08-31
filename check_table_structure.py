#!/usr/bin/env python3
"""
Script pour vérifier la structure de la table gpd_gares_ref
"""

import psycopg2
import os

def check_table_structure():
    """Vérifier la structure de la table gpd_gares_ref"""
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        # Vérifier les colonnes de gpd_gares_ref
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'gpd_gares_ref' 
            AND table_schema = 'gpr' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("Colonnes de gpd_gares_ref:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # Vérifier quelques données
        cursor.execute("SELECT * FROM gpr.gpd_gares_ref LIMIT 1")
        sample_data = cursor.fetchone()
        if sample_data:
            print(f"\nExemple de données:")
            print(f"  {sample_data}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_table_structure()
