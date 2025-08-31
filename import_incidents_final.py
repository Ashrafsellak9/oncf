#!/usr/bin/env python3
"""
Import final des incidents avec les bons indices
"""

import pandas as pd
import psycopg2
import os

def import_incidents_final():
    """Import final des incidents"""
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
        
        # Activer PostGIS
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        conn.commit()
        print("✅ PostGIS activé")
        
        # Créer la table si elle n'existe pas
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ge_evenement (
            id SERIAL PRIMARY KEY,
            gid INTEGER,
            date_debut TIMESTAMP,
            date_fin TIMESTAMP,
            heure_debut TIME,
            heure_fin TIME,
            date_creation TIMESTAMP,
            type_id INTEGER,
            statut VARCHAR(50),
            description TEXT,
            resume TEXT,
            localisation_id INTEGER,
            source_id INTEGER,
            sous_type_id INTEGER,
            systeme_id INTEGER,
            entite_id INTEGER,
            site_surete_id INTEGER,
            axe VARCHAR(100),
            section VARCHAR(100),
            gare VARCHAR(100),
            pk_debut DECIMAL(10,3),
            pk_fin DECIMAL(10,3),
            geometrie GEOMETRY(POINT, 4326),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ Table créée")
        
        # Vider la table
        cursor.execute("TRUNCATE TABLE ge_evenement RESTART IDENTITY CASCADE;")
        conn.commit()
        print("🗑️ Table vidée")
        
        # Lire le CSV
        csv_file = "sql_data/incidents.csv"
        df = pd.read_csv(csv_file, header=None)
        print(f"📖 {len(df)} incidents trouvés")
        
        # Insérer les données
        inserted_count = 0
        
        for index, row in df.iterrows():
            try:
                # Extraire les données avec les bons indices basés sur la structure observée
                gid = int(row[0]) if pd.notna(row[0]) else None
                date_debut = pd.to_datetime(row[1]) if pd.notna(row[1]) else None
                date_fin = pd.to_datetime(row[2]) if pd.notna(row[2]) else None
                date_creation = pd.to_datetime(row[5]) if pd.notna(row[5]) else None
                type_id = int(row[6]) if pd.notna(row[6]) else None
                statut = str(row[7]) if pd.notna(row[7]) else None
                description = str(row[8]) if pd.notna(row[8]) else None
                resume = str(row[9]) if pd.notna(row[9]) else None
                localisation_id = int(row[10]) if pd.notna(row[10]) else None
                source_id = int(row[11]) if pd.notna(row[11]) else None
                sous_type_id = int(row[12]) if pd.notna(row[12]) else None
                systeme_id = int(row[13]) if pd.notna(row[13]) else None
                entite_id = int(row[14]) if pd.notna(row[14]) else None
                site_surete_id = int(row[15]) if pd.notna(row[15]) else None
                axe = str(row[16]) if pd.notna(row[16]) else None
                section = str(row[17]) if pd.notna(row[17]) else None
                gare = str(row[18]) if pd.notna(row[18]) else None
                pk_debut = float(row[19]) if pd.notna(row[19]) else None
                pk_fin = float(row[20]) if pd.notna(row[20]) else None
                
                # Gérer les heures (colonnes 8 et 9)
                heure_debut = str(row[8]) if pd.notna(row[8]) and ':' in str(row[8]) else None
                heure_fin = str(row[9]) if pd.notna(row[9]) and ':' in str(row[9]) else None
                
                # Insérer
                insert_sql = """
                INSERT INTO ge_evenement (
                    gid, date_debut, date_fin, heure_debut, heure_fin, date_creation, 
                    type_id, statut, description, resume, localisation_id, source_id, 
                    sous_type_id, systeme_id, entite_id, site_surete_id, axe, section, 
                    gare, pk_debut, pk_fin
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                
                cursor.execute(insert_sql, (
                    gid, date_debut, date_fin, heure_debut, heure_fin, date_creation,
                    type_id, statut, description, resume, localisation_id, source_id,
                    sous_type_id, systeme_id, entite_id, site_surete_id, axe, section,
                    gare, pk_debut, pk_fin
                ))
                
                inserted_count += 1
                
                if inserted_count % 50 == 0:
                    conn.commit()
                    print(f"📊 {inserted_count} incidents importés...")
                    
            except Exception as e:
                print(f"⚠️ Erreur incident {index + 1}: {e}")
                print(f"   GID: {row[0]}, Type: {row[6]}, Statut: {row[7]}")
                continue
        
        conn.commit()
        print(f"✅ {inserted_count} incidents importés avec succès!")
        
        # Vérifier
        cursor.execute("SELECT COUNT(*) FROM ge_evenement;")
        count = cursor.fetchone()[0]
        print(f"📊 Total dans la base: {count}")
        
        # Statistiques
        cursor.execute("SELECT statut, COUNT(*) FROM ge_evenement GROUP BY statut;")
        stats = cursor.fetchall()
        print("\n📈 Par statut:")
        for statut, count in stats:
            print(f"   {statut}: {count}")
        
        # Types d'incidents
        cursor.execute("SELECT type_id, COUNT(*) FROM ge_evenement GROUP BY type_id ORDER BY COUNT(*) DESC LIMIT 5;")
        types = cursor.fetchall()
        print("\n📊 Top 5 types d'incidents:")
        for type_id, count in types:
            print(f"   Type {type_id}: {count}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_incidents_final()
