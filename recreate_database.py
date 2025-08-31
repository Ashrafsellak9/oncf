#!/usr/bin/env python3
"""
Recréation de la base de données proprement
"""

import psycopg2

def recreate_database():
    """Recréer la base de données proprement"""
    try:
        # Connexion à postgres pour supprimer et recréer la base
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="postgres",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("🔄 Recréation de la base de données")
        print("=" * 50)
        
        # Supprimer la base existante
        print("🗑️ Suppression de la base oncf_achraf...")
        cursor.execute("DROP DATABASE IF EXISTS oncf_achraf;")
        print("✅ Base supprimée")
        
        # Créer une nouvelle base
        print("🏗️ Création de la nouvelle base oncf_achraf...")
        cursor.execute("CREATE DATABASE oncf_achraf;")
        print("✅ Base créée")
        
        conn.close()
        
        # Connexion à la nouvelle base
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Activer PostGIS
        print("🔧 Activation de PostGIS...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        conn.commit()
        print("✅ PostGIS activé")
        
        # Créer la table users
        print("👥 Création de la table users...")
        create_users_sql = """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            role VARCHAR(20) DEFAULT 'user',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_users_sql)
        conn.commit()
        print("✅ Table users créée")
        
        # Créer la table ge_evenement
        print("🚨 Création de la table ge_evenement...")
        create_incidents_sql = """
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
        cursor.execute(create_incidents_sql)
        conn.commit()
        print("✅ Table ge_evenement créée")
        
        # Créer les index
        print("📊 Création des index...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_type_id ON ge_evenement(type_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_statut ON ge_evenement(statut);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_date_debut ON ge_evenement(date_debut);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_localisation_id ON ge_evenement(localisation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_geometrie ON ge_evenement USING GIST(geometrie);")
        conn.commit()
        print("✅ Index créés")
        
        # Créer l'utilisateur admin
        print("👤 Création de l'utilisateur admin...")
        from werkzeug.security import generate_password_hash
        admin_password = generate_password_hash('admin123')
        
        insert_admin_sql = """
        INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active)
        VALUES ('admin', 'admin@oncf.ma', %s, 'Administrateur', 'ONCF', 'admin', TRUE)
        ON CONFLICT (username) DO NOTHING;
        """
        cursor.execute(insert_admin_sql, (admin_password,))
        conn.commit()
        print("✅ Utilisateur admin créé")
        
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
        
        print(f"\n✅ Base de données prête pour l'import!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    recreate_database()
