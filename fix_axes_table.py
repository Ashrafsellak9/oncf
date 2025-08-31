import psycopg2
import pandas as pd
import os

def fix_axes_table():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Recréer la table graphe_arc avec la bonne structure
        cursor.execute("""
            DROP TABLE IF EXISTS gpr.graphe_arc CASCADE;
        """)
        
        cursor.execute("""
            CREATE TABLE gpr.graphe_arc (
                id SERIAL PRIMARY KEY,
                axe_id INTEGER,
                nom_axe VARCHAR(300),
                pk_debut NUMERIC(15,6),
                pk_fin NUMERIC(15,6),
                plod VARCHAR(100),
                plof VARCHAR(100),
                absd NUMERIC(15,6),
                absf NUMERIC(15,6),
                geometrie TEXT
            );
        """)
        
        print("✅ Table gpr.graphe_arc recréée avec la bonne structure")
        
        # Lire le fichier CSV
        csv_file = "sql_data/axes.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return
            
        # Lire le CSV avec pandas
        df = pd.read_csv(csv_file, header=None)
        print(f"📊 Structure du fichier axes.csv: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # Fonction pour nettoyer les données
        def safe_int(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return int(value)
            except:
                return None
                
        def safe_float(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return float(value)
            except:
                return None
                
        def safe_str(value, max_length=300):
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
                # Extraire les données avec la bonne structure
                axe_id = safe_int(row[0]) if len(row) > 0 else None
                nom_axe = safe_str(row[1], 300) if len(row) > 1 else None  # Nom de l'axe
                pk_debut = safe_float(row[2]) if len(row) > 2 else None
                pk_fin = safe_float(row[3]) if len(row) > 3 else None
                plod = safe_str(row[4], 100) if len(row) > 4 else None
                plof = safe_str(row[5], 100) if len(row) > 5 else None
                absd = safe_float(row[6]) if len(row) > 6 else None
                absf = safe_float(row[7]) if len(row) > 7 else None
                geometrie = safe_str(row[8], 1000) if len(row) > 8 else None
                
                cursor.execute("""
                    INSERT INTO gpr.graphe_arc 
                    (axe_id, nom_axe, pk_debut, pk_fin, plod, plof, absd, absf, geometrie)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (axe_id, nom_axe, pk_debut, pk_fin, plod, plof, absd, absf, geometrie))
                
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
        
        # Afficher quelques exemples
        cursor.execute("""
            SELECT axe_id, nom_axe, pk_debut, pk_fin, plod, plof
            FROM gpr.graphe_arc 
            LIMIT 10
        """)
        
        print("\n📋 Exemples d'axes importés:")
        for row in cursor.fetchall():
            print(f"   - ID: {row[0]}, Nom: {row[1]}, PK Début: {row[2]}, PK Fin: {row[3]}, PLOD: {row[4]}, PLOF: {row[5]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_axes_table()
