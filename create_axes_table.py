import psycopg2
import pandas as pd
import os

def create_axes_table():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Créer la table graphe_arc
        cursor.execute("""
            DROP TABLE IF EXISTS gpr.graphe_arc CASCADE;
        """)
        
        cursor.execute("""
            CREATE TABLE gpr.graphe_arc (
                id SERIAL PRIMARY KEY,
                axe VARCHAR(200),
                cumuld NUMERIC(15,6),
                cumulf NUMERIC(15,6),
                plod VARCHAR(100),
                absd NUMERIC(15,6),
                plof VARCHAR(100),
                absf NUMERIC(15,6),
                geometrie TEXT
            );
        """)
        
        print("✅ Table gpr.graphe_arc créée")
        
        # Lire le fichier CSV
        csv_file = "sql_data/axes.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return
            
        # Lire le CSV avec pandas
        df = pd.read_csv(csv_file, header=None)
        print(f"📊 Structure du fichier axes.csv: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # Fonction pour nettoyer les données
        def safe_float(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return float(value)
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
                cumuld = safe_float(row[1])
                cumulf = safe_float(row[2])
                plod = safe_str(row[3], 100)
                absd = safe_float(row[4])
                plof = safe_str(row[5], 100)
                absf = safe_float(row[6])
                geometrie = safe_str(row[7], 1000) if len(row) > 7 else None
                
                cursor.execute("""
                    INSERT INTO gpr.graphe_arc 
                    (axe, cumuld, cumulf, plod, absd, plof, absf, geometrie)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (axe, cumuld, cumulf, plod, absd, plof, absf, geometrie))
                
                success_count += 1
                
                if success_count % 10 == 0:
                    print(f"📥 Importé {success_count} axes...")
                    
            except Exception as e:
                error_count += 1
                print(f"⚠️  Erreur ligne {index + 1}: {e}")
                continue
        
        conn.commit()
        
        # Vérifier l'import
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc;")
        count = cursor.fetchone()[0]
        print(f"\n✅ Import terminé: {count} axes importés avec succès")
        print(f"❌ Erreurs: {error_count}")
        
        # Statistiques par axe
        cursor.execute("""
            SELECT axe, COUNT(*) 
            FROM gpr.graphe_arc 
            GROUP BY axe 
            ORDER BY COUNT(*) DESC
        """)
        
        print("\n📊 Statistiques par axe:")
        for axe, count in cursor.fetchall():
            print(f"   - {axe}: {count} segments")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    create_axes_table()
