#!/usr/bin/env python3
"""
Correction de la table des incidents
"""

import psycopg2

def fix_incidents_table():
    """Corriger la table des incidents"""
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
        
        print("🔧 Correction de la table des incidents")
        print("=" * 50)
        
        # Supprimer la table existante
        print("🗑️ Suppression de la table ge_evenement existante...")
        cursor.execute("DROP TABLE IF EXISTS ge_evenement CASCADE;")
        conn.commit()
        print("✅ Table supprimée")
        
        # Activer PostGIS
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        conn.commit()
        print("✅ PostGIS activé")
        
        # Créer la table proprement
        create_table_sql = """
        CREATE TABLE ge_evenement (
            id SERIAL PRIMARY KEY,
            gid INTEGER,
            date_debut TIMESTAMP,
            date_fin TIMESTAMP,
            heure_debut TIME,
            heure_fin TIME,
            date_creation TIMESTAMP,
            type_id INTEGER,
            statut VARCHAR(50),
            description TEXT,
            resume TEXT,
            localisation_id INTEGER,
            source_id INTEGER,
            sous_type_id INTEGER,
            systeme_id INTEGER,
            entite_id INTEGER,
            site_surete_id INTEGER,
            axe VARCHAR(100),
            section VARCHAR(100),
            gare VARCHAR(100),
            pk_debut DECIMAL(10,3),
            pk_fin DECIMAL(10,3),
            geometrie GEOMETRY(POINT, 4326),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ Table ge_evenement créée proprement")
        
        # Créer les index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_type_id ON ge_evenement(type_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_statut ON ge_evenement(statut);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_date_debut ON ge_evenement(date_debut);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_localisation_id ON ge_evenement(localisation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_geometrie ON ge_evenement USING GIST(geometrie);")
        conn.commit()
        print("✅ Index créés")
        
        # Vérifier la structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'ge_evenement' 
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print(f"\n🔧 Structure de la table ge_evenement:")
        for col in columns:
            print(f"   {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        print(f"\n✅ Table ge_evenement prête pour l'import!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_incidents_table()
