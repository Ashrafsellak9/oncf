import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_localisation_structure():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        # Vérifier la structure de ge_localisation
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'gpr' AND table_name = 'ge_localisation'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print("Structure de la table gpr.ge_localisation:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # Vérifier s'il y a des données
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_localisation")
        count = cursor.fetchone()[0]
        print(f"\nNombre de localisations: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, nom, type_localisation FROM gpr.ge_localisation LIMIT 5")
            locations = cursor.fetchall()
            print("\nPremières localisations:")
            for loc in locations:
                print(f"  - ID: {loc[0]}, Nom: {loc[1]}, Type: {loc[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f'Erreur: {e}')

if __name__ == '__main__':
    check_localisation_structure()
