#!/usr/bin/env python3
"""
Vérification de toutes les tables dans la base de données
"""

import psycopg2

def check_all_tables():
    """Vérifier toutes les tables dans la base de données"""
    try:
        # Connexion
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres",
            port="5432"
        )
        cursor = conn.cursor()
        
        print("🔍 Vérification de toutes les tables dans la base de données")
        print("=" * 70)
        
        # Lister toutes les tables
        cursor.execute("""
            SELECT table_name, table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print("📋 Toutes les tables:")
        for table in tables:
            print(f"   - {table[0]} ({table[1]})")
        
        # Vérifier les vues
        cursor.execute("""
            SELECT viewname 
            FROM pg_views 
            WHERE schemaname = 'public';
        """)
        views = cursor.fetchall()
        
        if views:
            print(f"\n👁️ Vues trouvées:")
            for view in views:
                print(f"   - {view[0]}")
        
        # Vérifier les tables avec des colonnes dupliquées
        print(f"\n🔍 Vérification des colonnes dupliquées:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"""
                SELECT column_name, COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                GROUP BY column_name 
                HAVING COUNT(*) > 1;
            """)
            duplicates = cursor.fetchall()
            if duplicates:
                print(f"   ❌ {table_name} a des colonnes dupliquées:")
                for col, count in duplicates:
                    print(f"      - {col} ({count} fois)")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_all_tables()
