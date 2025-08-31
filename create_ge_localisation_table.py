import psycopg2
import pandas as pd
import os

def create_ge_localisation_table():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Créer la table ge_localisation
        cursor.execute("""
            DROP TABLE IF EXISTS gpr.ge_localisation CASCADE;
        """)
        
        cursor.execute("""
            CREATE TABLE gpr.ge_localisation (
                id SERIAL PRIMARY KEY,
                autre VARCHAR(500),
                commentaire TEXT,
                type_localisation VARCHAR(200),
                type_pk VARCHAR(200),
                pk_debut VARCHAR(200),
                pk_fin VARCHAR(200),
                gare_debut_id VARCHAR(200),
                gare_fin_id VARCHAR(200),
                evenement_id INTEGER,
                user_id INTEGER
            );
        """)
        
        print("✅ Table gpr.ge_localisation créée")
        
        # Lire le fichier CSV
        csv_file = "sql_data/localisation.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return
            
        # Lire le CSV avec pandas
        df = pd.read_csv(csv_file, header=None)
        print(f"📊 Structure du fichier localisation.csv: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # Fonction pour nettoyer les données
        def safe_int(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return int(value)
            except:
                return None
                
        def safe_str(value, max_length=500):
            if pd.isna(value) or value == '':
                return None
            str_value = str(value)
            if len(str_value) > max_length:
                return str_value[:max_length]
            return str_value
        
        # Importer les données ligne par ligne
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Extraire les données avec gestion d'erreur
                autre = safe_str(row[0], 500) if len(row) > 0 else None
                commentaire = safe_str(row[1], 1000) if len(row) > 1 else None
                type_localisation = safe_str(row[2], 200) if len(row) > 2 else None
                type_pk = safe_str(row[3], 200) if len(row) > 3 else None
                pk_debut = safe_str(row[4], 200) if len(row) > 4 else None
                pk_fin = safe_str(row[5], 200) if len(row) > 5 else None
                gare_debut_id = safe_str(row[6], 200) if len(row) > 6 else None
                gare_fin_id = safe_str(row[7], 200) if len(row) > 7 else None
                evenement_id = safe_int(row[8]) if len(row) > 8 else None
                user_id = safe_int(row[9]) if len(row) > 9 else None
                
                cursor.execute("""
                    INSERT INTO gpr.ge_localisation 
                    (autre, commentaire, type_localisation, type_pk, pk_debut, pk_fin, 
                     gare_debut_id, gare_fin_id, evenement_id, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (autre, commentaire, type_localisation, type_pk, pk_debut, pk_fin, 
                      gare_debut_id, gare_fin_id, evenement_id, user_id))
                
                success_count += 1
                
                if success_count % 50 == 0:
                    print(f"📥 Importé {success_count} localisations...")
                    
            except Exception as e:
                error_count += 1
                print(f"⚠️  Erreur ligne {index + 1}: {e}")
                continue
        
        conn.commit()
        
        # Vérifier l'import
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_localisation;")
        count = cursor.fetchone()[0]
        print(f"\n✅ Import terminé: {count} localisations importées avec succès")
        print(f"❌ Erreurs: {error_count}")
        
        # Afficher quelques exemples
        cursor.execute("""
            SELECT id, autre, type_localisation, pk_debut, pk_fin, evenement_id
            FROM gpr.ge_localisation 
            LIMIT 5
        """)
        
        print("\n📋 Exemples de localisations importées:")
        for row in cursor.fetchall():
            print(f"   - ID: {row[0]}, Autre: {row[1]}, Type: {row[2]}, PK Début: {row[3]}, PK Fin: {row[4]}, Événement: {row[5]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    create_ge_localisation_table()
