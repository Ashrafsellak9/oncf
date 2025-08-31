#!/usr/bin/env python3
"""
Script pour vérifier la structure des tables de référence
"""

import psycopg2
import os

def check_reference_tables():
    """Vérifier la structure des tables de référence"""
    
    print("🔍 Vérification de la structure des tables de référence")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        tables = [
            'gpr.ref_types',
            'gpr.ref_sous_types', 
            'gpr.ref_systemes',
            'gpr.ref_sources',
            'gpr.ref_entites'
        ]
        
        for table in tables:
            print(f"\n📋 Table: {table}")
            print("-" * 40)
            
            # Vérifier la structure
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = '{table.split('.')[0]}' 
                AND table_name = '{table.split('.')[1]}'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            if columns:
                print("   Colonnes:")
                for col in columns:
                    print(f"      - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            else:
                print("   ❌ Table non trouvée")
            
            # Vérifier le nombre d'enregistrements
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   📊 Nombre d'enregistrements: {count}")
                
                if count > 0:
                    # Afficher quelques exemples
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    examples = cursor.fetchall()
                    print("   📝 Exemples:")
                    for i, example in enumerate(examples, 1):
                        print(f"      {i}. {example}")
                        
            except Exception as e:
                print(f"   ❌ Erreur lors du comptage: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    check_reference_tables()
