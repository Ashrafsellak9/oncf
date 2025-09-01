import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_schema():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        # Vérifier le schéma actuel
        cursor.execute("SELECT current_schema()")
        schema = cursor.fetchone()[0]
        print(f'Schéma actuel: {schema}')
        
        # Chercher la table ge_evenement dans tous les schémas
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name = 'ge_evenement'
        """)
        tables = cursor.fetchall()
        print(f'\nTables ge_evenement trouvées:')
        for table in tables:
            print(f'  - Schéma: {table[0]}, Table: {table[1]}')
        
        # Chercher toutes les tables contenant "evenement" ou "incident"
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name LIKE '%evenement%' OR table_name LIKE '%incident%'
            ORDER BY table_schema, table_name
        """)
        related_tables = cursor.fetchall()
        print(f'\nTables liées aux événements/incidents:')
        for table in related_tables:
            print(f'  - Schéma: {table[0]}, Table: {table[1]}')
        
        # Vérifier le schéma gpr
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'gpr')")
        gpr_exists = cursor.fetchone()[0]
        print(f'\nSchéma gpr existe: {gpr_exists}')
        
        if gpr_exists:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'gpr'
                ORDER BY table_name
            """)
            gpr_tables = cursor.fetchall()
            print(f'\nTables dans le schéma gpr:')
            for table in gpr_tables:
                print(f'  - {table[0]}')
        
        conn.close()
        
    except Exception as e:
        print(f'Erreur: {e}')

if __name__ == '__main__':
    check_schema()
