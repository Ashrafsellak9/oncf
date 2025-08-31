#!/usr/bin/env python3
"""
Import des données d'incidents depuis incidents.csv
"""

import pandas as pd
import psycopg2
import os
from datetime import datetime
import sys

def connect_to_database():
    """Connexion à la base de données"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def create_incidents_table(conn):
    """Créer la table ge_evenement si elle n'existe pas"""
    try:
        cursor = conn.cursor()
        
        # Activer l'extension PostGIS
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        conn.commit()
        print("✅ Extension PostGIS activée")
        
        # Créer la table ge_evenement
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS ge_evenement (
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
        print("✅ Table ge_evenement créée/vérifiée")
        
        # Créer un index sur les colonnes importantes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_type_id ON ge_evenement(type_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_statut ON ge_evenement(statut);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_date_debut ON ge_evenement(date_debut);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_localisation_id ON ge_evenement(localisation_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_evenement_geometrie ON ge_evenement USING GIST(geometrie);")
        
        conn.commit()
        print("✅ Index créés")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table: {e}")
        conn.rollback()

def import_incidents_data(conn):
    """Importer les données d'incidents depuis le fichier CSV"""
    try:
        # Lire le fichier CSV
        csv_file = "sql_data/incidents.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return
        
        print(f"📖 Lecture du fichier {csv_file}...")
        
        # Définir les colonnes du CSV
        columns = [
            'gid', 'date_debut', 'date_fin', 'heure_debut', 'heure_fin', 
            'date_creation', 'type_id', 'statut', 'description', 'resume',
            'localisation_id', 'source_id', 'sous_type_id', 'systeme_id',
            'entite_id', 'site_surete_id', 'axe', 'section', 'gare',
            'pk_debut', 'pk_fin', 'geometrie', 'col23', 'col24', 'col25'
        ]
        
        # Lire le CSV avec pandas
        df = pd.read_csv(csv_file, names=columns, header=None)
        print(f"✅ {len(df)} incidents trouvés dans le fichier CSV")
        
        # Nettoyer et préparer les données
        cursor = conn.cursor()
        
        # Vider la table existante
        cursor.execute("TRUNCATE TABLE ge_evenement RESTART IDENTITY CASCADE;")
        print("🗑️ Table ge_evenement vidée")
        
        # Insérer les données
        inserted_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Préparer les données en utilisant les indices corrects
                gid = row[0] if pd.notna(row[0]) else None
                date_debut = pd.to_datetime(row[1]) if pd.notna(row[1]) else None
                date_fin = pd.to_datetime(row[2]) if pd.notna(row[2]) else None
                heure_debut = str(row[8]) if pd.notna(row[8]) else None
                heure_fin = str(row[9]) if pd.notna(row[9]) else None
                date_creation = pd.to_datetime(row[5]) if pd.notna(row[5]) else None
                type_id = int(row[6]) if pd.notna(row[6]) else None
                statut = str(row[7]) if pd.notna(row[7]) else None
                description = str(row[8]) if pd.notna(row[8]) else None
                resume = str(row[9]) if pd.notna(row[9]) else None
                localisation_id = int(row[10]) if pd.notna(row[10]) else None
                source_id = int(row[11]) if pd.notna(row[11]) else None
                sous_type_id = int(row[12]) if pd.notna(row[12]) else None
                systeme_id = int(row[13]) if pd.notna(row[13]) else None
                entite_id = int(row[14]) if pd.notna(row[14]) else None
                site_surete_id = int(row[15]) if pd.notna(row[15]) else None
                axe = str(row[16]) if pd.notna(row[16]) else None
                section = str(row[17]) if pd.notna(row[17]) else None
                gare = str(row[18]) if pd.notna(row[18]) else None
                pk_debut = float(row[19]) if pd.notna(row[19]) else None
                pk_fin = float(row[20]) if pd.notna(row[20]) else None
                
                # Préparer la géométrie (pour l'instant NULL, sera mise à jour plus tard)
                geometrie = None
                
                # Insérer l'incident
                insert_sql = """
                INSERT INTO ge_evenement (
                    gid, date_debut, date_fin, heure_debut, heure_fin, date_creation,
                    type_id, statut, description, resume, localisation_id, source_id,
                    sous_type_id, systeme_id, entite_id, site_surete_id, axe, section,
                    gare, pk_debut, pk_fin, geometrie
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                
                cursor.execute(insert_sql, (
                    gid, date_debut, date_fin, heure_debut, heure_fin, date_creation,
                    type_id, statut, description, resume, localisation_id, source_id,
                    sous_type_id, systeme_id, entite_id, site_surete_id, axe, section,
                    gare, pk_debut, pk_fin, geometrie
                ))
                
                inserted_count += 1
                
                # Commit tous les 10 incidents pour éviter les problèmes de transaction
                if inserted_count % 10 == 0:
                    conn.commit()
                
                # Afficher le progrès tous les 50 incidents
                if inserted_count % 50 == 0:
                    print(f"📊 {inserted_count} incidents importés...")
                
            except Exception as e:
                error_count += 1
                print(f"⚠️ Erreur lors de l'import de l'incident {index + 1}: {e}")
                print(f"   Données: GID={gid}, Type={type_id}, Statut={statut}")
                continue
        
        conn.commit()
        print(f"✅ Import terminé: {inserted_count} incidents importés, {error_count} erreurs")
        
        # Vérifier le nombre d'incidents dans la table
        cursor.execute("SELECT COUNT(*) FROM ge_evenement;")
        count = cursor.fetchone()[0]
        print(f"📊 Total d'incidents dans la base: {count}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        conn.rollback()

def verify_import(conn):
    """Vérifier l'import des données"""
    try:
        cursor = conn.cursor()
        
        # Compter les incidents
        cursor.execute("SELECT COUNT(*) FROM ge_evenement;")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total d'incidents: {total_count}")
        
        # Statistiques par statut
        cursor.execute("""
            SELECT statut, COUNT(*) as count 
            FROM ge_evenement 
            GROUP BY statut 
            ORDER BY count DESC;
        """)
        status_stats = cursor.fetchall()
        print("\n📈 Statistiques par statut:")
        for statut, count in status_stats:
            print(f"   {statut}: {count}")
        
        # Statistiques par type
        cursor.execute("""
            SELECT type_id, COUNT(*) as count 
            FROM ge_evenement 
            GROUP BY type_id 
            ORDER BY count DESC 
            LIMIT 10;
        """)
        type_stats = cursor.fetchall()
        print("\n📈 Top 10 des types d'incidents:")
        for type_id, count in type_stats:
            print(f"   Type {type_id}: {count}")
        
        # Quelques exemples d'incidents
        cursor.execute("""
            SELECT id, gid, statut, description 
            FROM ge_evenement 
            ORDER BY id 
            LIMIT 5;
        """)
        examples = cursor.fetchall()
        print("\n📝 Exemples d'incidents:")
        for incident_id, gid, statut, description in examples:
            desc_short = description[:100] + "..." if len(description) > 100 else description
            print(f"   ID {incident_id} (GID {gid}): {statut} - {desc_short}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

def main():
    """Fonction principale"""
    print("🚀 Import des données d'incidents")
    print("=" * 50)
    
    # Connexion à la base de données
    conn = connect_to_database()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    try:
        # Créer la table si nécessaire
        create_incidents_table(conn)
        
        # Importer les données
        import_incidents_data(conn)
        
        # Vérifier l'import
        verify_import(conn)
        
        print("\n🎉 Import des incidents terminé avec succès!")
        print("\n💡 Pour tester:")
        print("1. Redémarrez l'application Flask")
        print("2. Connectez-vous avec admin/admin123")
        print("3. Allez sur la page /incidents")
        print("4. Vous devriez voir les incidents maintenant!")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
