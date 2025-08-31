#!/usr/bin/env python3
"""
Vérifier la structure de la table graphe_arc
"""

import psycopg2
import os

def check_graphe_arc_structure():
    """Vérifier la structure de la table graphe_arc"""
    
    print("🔍 Vérification de la structure de la table graphe_arc")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        # Vérifier la structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'gpr' 
            AND table_name = 'graphe_arc'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            print("   Colonnes de la table gpr.graphe_arc:")
            for col in columns:
                print(f"      - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        else:
            print("   ❌ Table non trouvée")
        
        # Vérifier le nombre d'enregistrements
        try:
            cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc")
            count = cursor.fetchone()[0]
            print(f"   📊 Nombre d'enregistrements: {count}")
            
            if count > 0:
                # Afficher quelques exemples
                cursor.execute("SELECT * FROM gpr.graphe_arc LIMIT 3")
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
    check_graphe_arc_structure()
