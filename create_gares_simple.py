import psycopg2
import pandas as pd
import os

def create_gares_simple():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Créer la table gpd_gares_ref avec des champs plus larges
        cursor.execute("""
            DROP TABLE IF EXISTS gpr.gpd_gares_ref CASCADE;
        """)
        
        cursor.execute("""
            CREATE TABLE gpr.gpd_gares_ref (
                id SERIAL PRIMARY KEY,
                axe VARCHAR(200),
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
                pk_fin INTEGER,
                distance INTEGER,
                ville VARCHAR(200),
                region VARCHAR(200)
            );
        """)
        
        print("✅ Table gpr.gpd_gares_ref créée")
        
        # Lire le fichier CSV
        csv_file = "sql_data/gares.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return
            
        # Lire le CSV avec pandas
        df = pd.read_csv(csv_file, header=None)
        print(f"📊 Structure du fichier gares.csv: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # Fonction pour nettoyer les données
        def safe_int(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return int(float(value))
            except:
                return None
                
        def safe_str(value, max_length=200):
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
                axe = safe_str(row[0], 200)
                nomgarefr = safe_str(row[1], 300)
                typegare = safe_str(row[2], 100)
                pk_debut = safe_int(row[3])
                geometrie = safe_str(row[4], 500)
                geometrie_dec = safe_str(row[5], 500)
                plod = safe_int(row[6])
                plof = safe_int(row[7])
                commentaire = safe_str(row[8], 1000)
                section = safe_str(row[9], 200)
                etat = safe_str(row[10], 100)
                code_gare = safe_str(row[11], 100)
                pk_fin = safe_int(row[12])
                distance = safe_int(row[13])
                ville = safe_str(row[14], 200)
                region = safe_str(row[15] if len(row) > 15 else None, 200)
                
                cursor.execute("""
                    INSERT INTO gpr.gpd_gares_ref 
                    (axe, nomgarefr, typegare, pk_debut, geometrie, geometrie_dec, 
                     plod, plof, commentaire, section, etat, code_gare, pk_fin, distance, ville, region)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (axe, nomgarefr, typegare, pk_debut, geometrie, geometrie_dec,
                      plod, plof, commentaire, section, etat, code_gare, pk_fin, distance, ville, region))
                
                success_count += 1
                
                if success_count % 10 == 0:
                    print(f"📥 Importé {success_count} gares...")
                    
            except Exception as e:
                error_count += 1
                print(f"⚠️  Erreur ligne {index + 1}: {e}")
                continue
        
        conn.commit()
        
        # Vérifier l'import
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref;")
        count = cursor.fetchone()[0]
        print(f"\n✅ Import terminé: {count} gares importées avec succès")
        print(f"❌ Erreurs: {error_count}")
        
        # Statistiques par axe
        cursor.execute("""
            SELECT axe, COUNT(*) 
            FROM gpr.gpd_gares_ref 
            GROUP BY axe 
            ORDER BY COUNT(*) DESC
        """)
        
        print("\n📊 Statistiques par axe:")
        for axe, count in cursor.fetchall():
            print(f"   - {axe}: {count} gares")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    create_gares_simple()
