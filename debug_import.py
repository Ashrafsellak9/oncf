#!/usr/bin/env python3
"""
Debug de l'import des incidents
"""

import pandas as pd
import psycopg2
import os

def test_import():
    """Test simple d'import"""
    try:
        # Connexion
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Lire le CSV
        csv_file = "sql_data/incidents.csv"
        df = pd.read_csv(csv_file, header=None)
        print(f"✅ {len(df)} incidents trouvés")
        
        # Tester avec le premier incident
        row = df.iloc[0]
        print(f"Premier incident: {row.tolist()}")
        
        # Préparer les données
        gid = row[0] if pd.notna(row[0]) else None
        date_debut = pd.to_datetime(row[1]) if pd.notna(row[1]) else None
        type_id = int(row[6]) if pd.notna(row[6]) else None
        statut = str(row[7]) if pd.notna(row[7]) else None
        description = str(row[8]) if pd.notna(row[8]) else None
        
        print(f"GID: {gid}")
        print(f"Date début: {date_debut}")
        print(f"Type ID: {type_id}")
        print(f"Statut: {statut}")
        print(f"Description: {description[:100]}...")
        
        # Test d'insertion simple
        insert_sql = """
        INSERT INTO ge_evenement (
            gid, date_debut, type_id, statut, description
        ) VALUES (
            %s, %s, %s, %s, %s
        )
        """
        
        params = (gid, date_debut, type_id, statut, description)
        print(f"Paramètres: {params}")
        
        cursor.execute(insert_sql, params)
        conn.commit()
        print("✅ Insertion réussie!")
        
        # Vérifier
        cursor.execute("SELECT COUNT(*) FROM ge_evenement;")
        count = cursor.fetchone()[0]
        print(f"📊 Total d'incidents: {count}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_import()
