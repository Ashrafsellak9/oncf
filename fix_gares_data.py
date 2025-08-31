import psycopg2
import pandas as pd
import os
from psycopg2 import sql

def fix_gares_data():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Supprimer et recréer la table
        print("🗑️ Suppression de la table existante...")
        cursor.execute("DROP TABLE IF EXISTS gpr.gpd_gares_ref CASCADE;")
        
        print("🏗️ Création de la nouvelle table...")
        cursor.execute("""
            CREATE TABLE gpr.gpd_gares_ref (
                id SERIAL PRIMARY KEY,
                nomgarefr VARCHAR(300),
                typegare VARCHAR(100),
                pk_debut INTEGER,
                geometrie TEXT,
                geometrie_dec TEXT,
                plod INTEGER,
                plof INTEGER,
                commentaire TEXT,
                section VARCHAR(200),
                etat VARCHAR(100),
                code_gare VARCHAR(100),
                type_commercial VARCHAR(100),
                distance INTEGER,
                ville VARCHAR(200),
                region VARCHAR(200),
                statut VARCHAR(100)
            );
        """)
        
        # Lire le fichier CSV
        csv_file = "sql_data/gares.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return
            
        print("📖 Lecture du fichier CSV...")
        df = pd.read_csv(csv_file, header=None)
        
        print("📝 Insertion des données avec le bon mapping...")
        insert_query = sql.SQL("""
            INSERT INTO gpr.gpd_gares_ref 
            (nomgarefr, typegare, pk_debut, geometrie, geometrie_dec, plod, plof, commentaire, 
             section, etat, code_gare, type_commercial, distance, ville, region, statut)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)
        
        for index, row in df.iterrows():
            nomgarefr = str(row[1]) if pd.notna(row[1]) else None
            typegare = str(row[2]) if pd.notna(row[2]) else None
            pk_debut = int(row[3]) if pd.notna(row[3]) else None
            geometrie = str(row[4]) if pd.notna(row[4]) else None
            geometrie_dec = str(row[5]) if pd.notna(row[5]) else None
            plod = int(row[6]) if pd.notna(row[6]) and str(row[6]).isdigit() else None
            plof = int(row[7]) if pd.notna(row[7]) and str(row[7]).isdigit() else None
            commentaire = str(row[8]) if pd.notna(row[8]) else None
            section = str(row[9]) if pd.notna(row[9]) else None
            etat = str(row[10]) if pd.notna(row[10]) else None
            code_gare = str(row[11]) if pd.notna(row[11]) else None
            type_commercial = str(row[12]) if pd.notna(row[12]) else None
            distance = int(row[13]) if pd.notna(row[13]) and str(row[13]).isdigit() else None
            ville = str(row[14]) if pd.notna(row[14]) else None
            region = str(row[15]) if pd.notna(row[15]) else None
            statut = str(row[16]) if pd.notna(row[16]) else None
            
            cursor.execute(insert_query, (
                nomgarefr, typegare, pk_debut, geometrie, geometrie_dec, plod, plof, commentaire,
                section, etat, code_gare, type_commercial, distance, ville, region, statut
            ))
            
            if (index + 1) % 50 == 0:
                conn.commit()
                print(f"✅ {index + 1} gares importées...")
        
        conn.commit()
        
        # Vérifier les données
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref;")
        count = cursor.fetchone()[0]
        print(f"✅ {count} gares importées avec succès")
        
        # Afficher quelques exemples
        cursor.execute("""
            SELECT id, nomgarefr, typegare, etat, code_gare, ville, region, section
            FROM gpr.gpd_gares_ref 
            ORDER BY id 
            LIMIT 5
        """)
        
        gares = cursor.fetchall()
        print("\n📋 Exemples de gares importées:")
        for gare in gares:
            print(f"   - ID: {gare[0]}, Nom: {gare[1]}, Type: {gare[2]}, État: {gare[3]}, Code: {gare[4]}, Ville: {gare[5]}, Région: {gare[6]}, Section: {gare[7]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_gares_data()
