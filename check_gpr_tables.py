import psycopg2
from psycopg2 import sql

def check_gpr_tables():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Vérifier les tables dans le schéma gpr
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'gpr'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print("Tables dans le schéma gpr:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Vérifier les tables dans le schéma public
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print("\nTables dans le schéma public:")
        for table in tables:
            print(f"  - {table[0]}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_gpr_tables()
