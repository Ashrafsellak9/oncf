#!/usr/bin/env python3
"""
Vérification des incidents dans la base de données
"""

import psycopg2

def check_database_incidents():
    """Vérifier les incidents dans la base de données"""
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
        
        print("🔍 Vérification des incidents dans la base de données")
        print("=" * 60)
        
        # Compter les incidents
        cursor.execute("SELECT COUNT(*) FROM ge_evenement;")
        count = cursor.fetchone()[0]
        print(f"📊 Total d'incidents dans la table: {count}")
        
        if count > 0:
            # Afficher quelques exemples
            cursor.execute("SELECT id, gid, type_id, statut, description FROM ge_evenement LIMIT 5;")
            incidents = cursor.fetchall()
            
            print(f"\n📋 Exemples d'incidents:")
            for incident in incidents:
                id, gid, type_id, statut, description = incident
                desc_short = description[:100] + "..." if description and len(description) > 100 else description
                print(f"   ID: {id}, GID: {gid}, Type: {type_id}, Statut: {statut}")
                print(f"   Description: {desc_short}")
                print()
            
            # Statistiques par statut
            cursor.execute("SELECT statut, COUNT(*) FROM ge_evenement GROUP BY statut;")
            stats = cursor.fetchall()
            print(f"📈 Répartition par statut:")
            for statut, count in stats:
                print(f"   {statut}: {count}")
            
            # Statistiques par type
            cursor.execute("SELECT type_id, COUNT(*) FROM ge_evenement GROUP BY type_id ORDER BY COUNT(*) DESC;")
            types = cursor.fetchall()
            print(f"\n📊 Répartition par type:")
            for type_id, count in types:
                print(f"   Type {type_id}: {count}")
        else:
            print("❌ Aucun incident trouvé dans la base de données")
        
        # Vérifier la structure de la table
        print(f"\n🔧 Structure de la table ge_evenement:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'ge_evenement' 
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database_incidents()
