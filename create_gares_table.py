import psycopg2
import pandas as pd
import os

def create_gares_table():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Créer la table gpd_gares_ref
        cursor.execute("""
            DROP TABLE IF EXISTS gpr.gpd_gares_ref CASCADE;
        """)
        
        cursor.execute("""
            CREATE TABLE gpr.gpd_gares_ref (
                id SERIAL PRIMARY KEY,
                axe VARCHAR(100),
                nomgarefr VARCHAR(200),
                typegare VARCHAR(50),
                pk_debut INTEGER,
                geometrie GEOMETRY(POINT, 3857),
                geometrie_dec GEOMETRY(POINT, 3857),
                plod INTEGER,
                plof INTEGER,
                commentaire TEXT,
                section VARCHAR(100),
                etat VARCHAR(50),
                code_gare VARCHAR(20),
                pk_fin INTEGER,
                distance INTEGER,
                ville VARCHAR(100),
                region VARCHAR(100)
            );
        """)
        
        print("✅ Table gpr.gpd_gares_ref créée")
        
        # Lire le fichier CSV
        csv_file = "sql_data/gares.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return
            
        # Lire le CSV avec pandas pour voir la structure
        df = pd.read_csv(csv_file, header=None)
        print(f"📊 Structure du fichier gares.csv: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        print(f"📋 Premières colonnes: {list(df.columns)}")
        
        # Afficher les premières lignes pour comprendre la structure
        print("\n📋 Premières lignes:")
        print(df.head())
        
        # Importer les données
        with open(csv_file, 'r', encoding='utf-8') as f:
            next(f)  # Skip header if exists
            for line_num, line in enumerate(f, 1):
                try:
                    # Split par virgule, mais gérer les virgules dans les champs
                    parts = line.strip().split(',')
                    
                    # Extraire les données selon la structure observée
                    if len(parts) >= 16:
                        axe = parts[0] if parts[0] else None
                        nomgarefr = parts[1] if parts[1] else None
                        typegare = parts[2] if parts[2] else None
                        pk_debut = int(parts[3]) if parts[3] and parts[3].isdigit() else None
                        geometrie = parts[4] if parts[4] else None
                        geometrie_dec = parts[5] if parts[5] else None
                        plod = int(parts[6]) if parts[6] and parts[6].isdigit() else None
                        plof = int(parts[7]) if parts[7] and parts[7].isdigit() else None
                        commentaire = parts[8] if parts[8] else None
                        section = parts[9] if parts[9] else None
                        etat = parts[10] if parts[10] else None
                        code_gare = parts[11] if parts[11] else None
                        pk_fin = int(parts[12]) if parts[12] and parts[12].isdigit() else None
                        distance = int(parts[13]) if parts[13] and parts[13].isdigit() else None
                        ville = parts[14] if parts[14] else None
                        region = parts[15] if parts[15] else None
                        
                        cursor.execute("""
                            INSERT INTO gpr.gpd_gares_ref 
                            (axe, nomgarefr, typegare, pk_debut, geometrie, geometrie_dec, 
                             plod, plof, commentaire, section, etat, code_gare, pk_fin, distance, ville, region)
                            VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 3857), ST_GeomFromText(%s, 3857),
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (axe, nomgarefr, typegare, pk_debut, geometrie, geometrie_dec,
                              plod, plof, commentaire, section, etat, code_gare, pk_fin, distance, ville, region))
                        
                        if line_num % 10 == 0:
                            print(f"📥 Importé {line_num} gares...")
                            
                except Exception as e:
                    print(f"⚠️  Erreur ligne {line_num}: {e}")
                    print(f"   Ligne: {line.strip()}")
                    continue
        
        conn.commit()
        
        # Vérifier l'import
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref;")
        count = cursor.fetchone()[0]
        print(f"\n✅ Import terminé: {count} gares importées")
        
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
    create_gares_table()
