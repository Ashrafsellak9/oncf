import psycopg2
import psycopg2.extras

def check_gares_structure():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Vérifier la structure de la table
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_schema = 'gpr' 
            AND table_name = 'gpd_gares_ref'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("📋 Structure de la table gpr.gpd_gares_ref:")
        for col in columns:
            print(f"   - {col['column_name']}: {col['data_type']}")
        
        # Vérifier les données
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total gares dans la table: {total}")
        
        if total > 0:
            # Voir les premières lignes
            cursor.execute("SELECT * FROM gpr.gpd_gares_ref LIMIT 3")
            rows = cursor.fetchall()
            print("\n📋 Premières lignes:")
            for i, row in enumerate(rows):
                print(f"   Ligne {i+1}: {dict(row)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_gares_structure()
