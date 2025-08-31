#!/usr/bin/env python3
"""
Création du schéma gpr et déplacement des tables
"""

import psycopg2

def fix_schema():
    """Créer le schéma gpr et déplacer les tables"""
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
        
        print("🔧 Création du schéma gpr et déplacement des tables")
        print("=" * 60)
        
        # Créer le schéma gpr
        print("📁 Création du schéma gpr...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS gpr;")
        conn.commit()
        print("✅ Schéma gpr créé")
        
        # Déplacer la table users vers le schéma gpr
        print("👥 Déplacement de la table users...")
        cursor.execute("""
            CREATE TABLE gpr.users AS 
            SELECT * FROM users;
        """)
        conn.commit()
        print("✅ Table users déplacée vers gpr.users")
        
        # Supprimer l'ancienne table users
        cursor.execute("DROP TABLE users;")
        conn.commit()
        print("✅ Ancienne table users supprimée")
        
        # Créer la table ge_evenement dans le schéma gpr
        print("🚨 Création de la table ge_evenement dans gpr...")
        cursor.execute("""
            CREATE TABLE gpr.ge_evenement (
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
                axe VARCHAR(500),
                section VARCHAR(500),
                gare VARCHAR(500),
                pk_debut DECIMAL(10,3),
                pk_fin DECIMAL(10,3),
                geometrie GEOMETRY(POINT, 4326),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("✅ Table ge_evenement créée dans gpr")
        
        # Créer les index
        print("📊 Création des index...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_type_id ON gpr.ge_evenement(type_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_statut ON gpr.ge_evenement(statut);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_date_debut ON gpr.ge_evenement(date_debut);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_localisation_id ON gpr.ge_evenement(localisation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_geometrie ON gpr.ge_evenement USING GIST(geometrie);")
        conn.commit()
        print("✅ Index créés")
        
        # Déplacer les incidents existants
        print("📋 Déplacement des incidents existants...")
        cursor.execute("""
            INSERT INTO gpr.ge_evenement (
                gid, date_debut, date_fin, heure_debut, heure_fin, date_creation,
                type_id, statut, description, resume, localisation_id, source_id,
                sous_type_id, systeme_id, entite_id, site_surete_id, axe, section,
                gare, pk_debut, pk_fin
            )
            SELECT 
                gid, date_debut, date_fin, heure_debut, heure_fin, date_creation,
                type_id, statut, description, resume, localisation_id, source_id,
                sous_type_id, systeme_id, entite_id, site_surete_id, axe, section,
                gare, pk_debut, pk_fin
            FROM ge_evenement;
        """)
        conn.commit()
        print("✅ Incidents déplacés vers gpr.ge_evenement")
        
        # Supprimer l'ancienne table ge_evenement
        cursor.execute("DROP TABLE ge_evenement;")
        conn.commit()
        print("✅ Ancienne table ge_evenement supprimée")
        
        # Vérifier les tables
        cursor.execute("""
            SELECT table_name, table_schema 
            FROM information_schema.tables 
            WHERE table_schema = 'gpr'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"\n📋 Tables dans le schéma gpr:")
        for table in tables:
            print(f"   - {table[1]}.{table[0]}")
        
        # Vérifier les incidents
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_evenement;")
        count = cursor.fetchone()[0]
        print(f"\n📊 Nombre d'incidents dans gpr.ge_evenement: {count}")
        
        # Vérifier les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM gpr.users;")
        count = cursor.fetchone()[0]
        print(f"👥 Nombre d'utilisateurs dans gpr.users: {count}")
        
        print(f"\n✅ Schéma gpr configuré avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_schema()
