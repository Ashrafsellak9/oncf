import psycopg2
import pandas as pd
import os

def create_ref_types_table():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Créer la table ref_types
        cursor.execute("""
            DROP TABLE IF EXISTS gpr.ref_types CASCADE;
        """)
        
        cursor.execute("""
            CREATE TABLE gpr.ref_types (
                id SERIAL PRIMARY KEY,
                date_maj TIMESTAMP,
                intitule VARCHAR(300),
                entite_type_id INTEGER,
                etat BOOLEAN DEFAULT true,
                deleted BOOLEAN DEFAULT false
            );
        """)
        
        print("✅ Table gpr.ref_types créée")
        
        # Lire le fichier CSV
        csv_file = "sql_data/ref_types.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return
            
        # Lire le CSV avec pandas
        df = pd.read_csv(csv_file, header=None)
        print(f"📊 Structure du fichier ref_types.csv: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # Fonction pour nettoyer les données
        def safe_int(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return int(value)
            except:
                return None
                
        def safe_str(value, max_length=300):
            if pd.isna(value) or value == '':
                return None
            str_value = str(value)
            if len(str_value) > max_length:
                return str_value[:max_length]
            return str_value
            
        def safe_bool(value):
            if pd.isna(value) or value == '':
                return True
            try:
                return bool(value)
            except:
                return True
        
        # Importer les données ligne par ligne
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Extraire les données avec gestion d'erreur
                date_maj = None  # On peut ajouter la logique pour parser la date si nécessaire
                intitule = safe_str(row[0], 300) if len(row) > 0 else None
                entite_type_id = safe_int(row[1]) if len(row) > 1 else None
                etat = safe_bool(row[2]) if len(row) > 2 else True
                deleted = safe_bool(row[3]) if len(row) > 3 else False
                
                cursor.execute("""
                    INSERT INTO gpr.ref_types 
                    (date_maj, intitule, entite_type_id, etat, deleted)
                    VALUES (%s, %s, %s, %s, %s)
                """, (date_maj, intitule, entite_type_id, etat, deleted))
                
                success_count += 1
                
                if success_count % 10 == 0:
                    print(f"📥 Importé {success_count} types...")
                    
            except Exception as e:
                error_count += 1
                print(f"⚠️  Erreur ligne {index + 1}: {e}")
                continue
        
        conn.commit()
        
        # Vérifier l'import
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_types;")
        count = cursor.fetchone()[0]
        print(f"\n✅ Import terminé: {count} types importés avec succès")
        print(f"❌ Erreurs: {error_count}")
        
        # Afficher quelques exemples
        cursor.execute("""
            SELECT id, intitule, entite_type_id, etat, deleted
            FROM gpr.ref_types 
            LIMIT 5
        """)
        
        print("\n📋 Exemples de types importés:")
        for row in cursor.fetchall():
            print(f"   - ID: {row[0]}, Intitulé: {row[1]}, Entité: {row[2]}, État: {row[3]}, Supprimé: {row[4]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    create_ref_types_table()
