#!/usr/bin/env python3
"""
Script pour supprimer et recréer toutes les tables sans contraintes FK
"""

import psycopg2
import os
import pandas as pd

def recreate_tables_without_fk():
    """Supprimer et recréer toutes les tables sans contraintes FK"""
    
    try:
        print("🔧 Suppression et recréation des tables sans contraintes FK")
        print("=" * 80)
        
        # Se connecter à la base de données
        print("\n🗄️ Connexion à la base de données...")
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 1. Supprimer toutes les tables existantes
        print("\n🗑️ Suppression des tables existantes...")
        tables_to_drop = [
            'gpr.ge_evenement',
            'gpr.ge_localisation', 
            'gpr.ref_site_surete',
            'gpr.ref_types',
            'gpr.ref_entites',
            'gpr.ref_sources',
            'gpr.ref_sous_types',
            'gpr.ref_systemes'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"   ✅ Table {table} supprimée")
            except Exception as e:
                print(f"   ⚠️  Erreur suppression {table}: {e}")
        
        # 2. Créer la table ref_entites
        print("\n🏢 Création de la table ref_entites...")
        cursor.execute("""
            CREATE TABLE gpr.ref_entites (
                id SERIAL PRIMARY KEY,
                intitule VARCHAR(255) NOT NULL
            )
        """)
        
        # 3. Créer la table ref_systemes
        print("🏢 Création de la table ref_systemes...")
        cursor.execute("""
            CREATE TABLE gpr.ref_systemes (
                id SERIAL PRIMARY KEY,
                date_maj TIMESTAMP,
                intitule VARCHAR(255) NOT NULL,
                entite_id INTEGER,
                etat VARCHAR(50),
                deleted BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 4. Créer la table ref_types
        print("🏢 Création de la table ref_types...")
        cursor.execute("""
            CREATE TABLE gpr.ref_types (
                id SERIAL PRIMARY KEY,
                date_maj TIMESTAMP,
                intitule VARCHAR(255) NOT NULL,
                system_id INTEGER,
                entite_type_id INTEGER,
                etat VARCHAR(50),
                deleted BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 5. Créer la table ref_sous_types
        print("🏢 Création de la table ref_sous_types...")
        cursor.execute("""
            CREATE TABLE gpr.ref_sous_types (
                id SERIAL PRIMARY KEY,
                date_maj TIMESTAMP,
                etat VARCHAR(50),
                type_id INTEGER,
                entitest_id INTEGER,
                intitule VARCHAR(255) NOT NULL,
                deleted BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 6. Créer la table ref_sources
        print("🏢 Création de la table ref_sources...")
        cursor.execute("""
            CREATE TABLE gpr.ref_sources (
                id SERIAL PRIMARY KEY,
                date_maj TIMESTAMP,
                etat VARCHAR(50),
                intitule VARCHAR(255) NOT NULL,
                entite_source_id INTEGER,
                deleted BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 7. Créer la table ref_site_surete
        print("🏢 Création de la table ref_site_surete...")
        cursor.execute("""
            CREATE TABLE gpr.ref_site_surete (
                id SERIAL PRIMARY KEY,
                intitule VARCHAR(255) NOT NULL
            )
        """)
        
        # 8. Créer la table ge_localisation
        print("🏢 Création de la table ge_localisation...")
        cursor.execute("""
            CREATE TABLE gpr.ge_localisation (
                id SERIAL PRIMARY KEY,
                autre TEXT,
                commentaire TEXT,
                datemaj TIMESTAMP,
                gare_debut_id INTEGER,
                gare_fin_id INTEGER,
                type_localisation VARCHAR(100),
                type_pk VARCHAR(50),
                user_id INTEGER,
                atelier_id INTEGER,
                embranchement_id INTEGER,
                evenement_id INTEGER,
                etablissement_id INTEGER,
                site_surete_id INTEGER,
                wilaya_id INTEGER,
                prefecture_id INTEGER,
                commune_id INTEGER,
                autorite_id INTEGER,
                pk_debut DECIMAL(10,3),
                pk_fin DECIMAL(10,3),
                zone_cloture VARCHAR(100)
            )
        """)
        
        # 9. Créer la table ge_evenement sans contraintes FK
        print("🏢 Création de la table ge_evenement...")
        cursor.execute("""
            CREATE TABLE gpr.ge_evenement (
                id SERIAL PRIMARY KEY,
                date_avis DATE,
                date_debut DATE,
                date_fin DATE,
                date_impact DATE,
                datemaj TIMESTAMP,
                entite VARCHAR(255),
                etat VARCHAR(100),
                heure_avis TIME,
                heure_debut TIME,
                heure_fin TIME,
                heure_impact TIME,
                impact_service TEXT,
                important BOOLEAN DEFAULT FALSE,
                inclure_commentaire BOOLEAN DEFAULT FALSE,
                rapport_journalier TEXT,
                resume TEXT,
                source_personne VARCHAR(255),
                user_id INTEGER,
                source_id INTEGER,
                sous_type_id INTEGER,
                system_id INTEGER,
                type_id INTEGER,
                extrait TEXT,
                rapport_hebdomadaire TEXT,
                fonction VARCHAR(255),
                commentaire TEXT,
                deleted BOOLEAN DEFAULT FALSE,
                responsabilite_id INTEGER,
                entite_id INTEGER,
                workflow_etape_id INTEGER,
                localisation_id INTEGER
            )
        """)
        
        print("   ✅ Toutes les tables créées avec succès (sans contraintes FK)")
        
        # 10. Insérer les données de ref_site_surete
        print("\n📝 Insertion des données ref_site_surete...")
        sites_surete = [
            (1, 'Pleine Ligne (DRIC)'),
            (2, 'Casa Voyageurs'),
            (3, 'Casa Port'),
            (4, 'Rabat-Agdal'),
            (5, 'Rabat CCR et Siège'),
            (6, 'Tanger'),
            (7, 'Fès'),
            (8, 'Sidi Kacem'),
            (9, 'Oujda'),
            (10, 'Marrakech')
        ]
        
        for site_id, intitule in sites_surete:
            cursor.execute("""
                INSERT INTO gpr.ref_site_surete (id, intitule) 
                VALUES (%s, %s)
            """, (site_id, intitule))
        
        print(f"   ✅ {len(sites_surete)} sites de sûreté insérés")
        
        # 11. Lire et insérer les données des incidents
        print("\n📖 Lecture du fichier CSV incidents...")
        csv_file = "sql_data/incidents.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return False
        
        # Lire le CSV avec les bonnes colonnes (31 colonnes)
        df = pd.read_csv(csv_file, header=None)
        
        print(f"   {len(df)} incidents trouvés dans le CSV")
        
        # 12. Insérer les données avec le bon mapping
        print("\n📝 Insertion des données incidents...")
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Mapping selon la vraie structure ge_evenement:
                # [id], [date_avis], [date_debut], [date_fin], [date_impact], [datemaj], 
                # [entite], [etat], [heure_avis], [heure_debut], [heure_fin], [heure_impact], 
                # [impact_service], [important], [inclure_commentaire], [rapport_journalier], 
                # [resume], [source_personne], [user_id], [source_id], [sous_type_id], 
                # [system_id], [type_id], [extrait], [rapport_hebdomadaire], [fonction], 
                # [commentaire], [deleted], [responsabilite_id], [entite_id], [workflow_etape_id]
                
                cursor.execute("""
                    INSERT INTO gpr.ge_evenement (
                        date_avis, date_debut, date_fin, date_impact, datemaj,
                        entite, etat, heure_avis, heure_debut, heure_fin, heure_impact,
                        impact_service, important, inclure_commentaire, rapport_journalier,
                        resume, source_personne, user_id, source_id, sous_type_id,
                        system_id, type_id, extrait, rapport_hebdomadaire, fonction,
                        commentaire, deleted, responsabilite_id, entite_id, workflow_etape_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    row[1] if pd.notna(row[1]) else None,  # date_avis
                    row[2] if pd.notna(row[2]) else None,  # date_debut
                    row[3] if pd.notna(row[3]) else None,  # date_fin
                    row[4] if pd.notna(row[4]) else None,  # date_impact
                    row[5] if pd.notna(row[5]) else None,  # datemaj
                    row[6] if pd.notna(row[6]) else None,  # entite
                    row[7] if pd.notna(row[7]) else None,  # etat
                    row[8] if pd.notna(row[8]) else None,  # heure_avis
                    row[9] if pd.notna(row[9]) else None,  # heure_debut
                    row[10] if pd.notna(row[10]) else None, # heure_fin
                    row[11] if pd.notna(row[11]) else None, # heure_impact
                    row[12] if pd.notna(row[12]) else None, # impact_service
                    row[13] if pd.notna(row[13]) else False, # important
                    row[14] if pd.notna(row[14]) else False, # inclure_commentaire
                    row[15] if pd.notna(row[15]) else None, # rapport_journalier
                    row[16] if pd.notna(row[16]) else None, # resume
                    row[17] if pd.notna(row[17]) else None, # source_personne
                    row[18] if pd.notna(row[18]) else None, # user_id
                    row[19] if pd.notna(row[19]) else None, # source_id
                    row[20] if pd.notna(row[20]) else None, # sous_type_id
                    row[21] if pd.notna(row[21]) else None, # system_id
                    row[22] if pd.notna(row[22]) else None, # type_id
                    row[23] if pd.notna(row[23]) else None, # extrait
                    row[24] if pd.notna(row[24]) else None, # rapport_hebdomadaire
                    row[25] if pd.notna(row[25]) else None, # fonction
                    row[26] if pd.notna(row[26]) else None, # commentaire
                    row[27] if pd.notna(row[27]) else False, # deleted
                    row[28] if pd.notna(row[28]) else None, # responsabilite_id
                    row[29] if pd.notna(row[29]) else None, # entite_id
                    row[30] if pd.notna(row[30]) else None  # workflow_etape_id
                ))
                
                success_count += 1
                
                if success_count % 50 == 0:
                    print(f"   {success_count} incidents insérés...")
                
            except Exception as e:
                error_count += 1
                print(f"   ❌ Erreur ligne {index + 1}: {e}")
                continue
        
        print(f"\n✅ {success_count} incidents insérés avec succès")
        if error_count > 0:
            print(f"⚠️  {error_count} erreurs rencontrées")
        
        # 13. Créer les localisations pour chaque incident
        print("\n📍 Création des localisations...")
        cursor.execute("""
            INSERT INTO gpr.ge_localisation (
                evenement_id, type_localisation, user_id
            )
            SELECT 
                id, 
                'incident' as type_localisation,
                1 as user_id
            FROM gpr.ge_evenement
        """)
        
        print(f"   {cursor.rowcount} localisations créées")
        
        # 14. Mettre à jour les localisation_id dans ge_evenement
        print("\n🔗 Mise à jour des localisation_id...")
        cursor.execute("""
            UPDATE gpr.ge_evenement e
            SET localisation_id = l.id
            FROM gpr.ge_localisation l
            WHERE l.evenement_id = e.id
        """)
        
        print(f"   {cursor.rowcount} localisation_id mis à jour")
        
        # 15. Vérifier le résultat
        print("\n✅ Vérification du résultat...")
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_evenement")
        total = cursor.fetchone()[0]
        print(f"   Total incidents: {total}")
        
        # Vérifier quelques exemples
        cursor.execute("""
            SELECT id, date_debut, heure_debut, resume, entite, etat, 
                   type_id, source_id, entite_id, localisation_id
            FROM gpr.ge_evenement 
            LIMIT 3
        """)
        
        incidents = cursor.fetchall()
        for i, incident in enumerate(incidents):
            print(f"\n   Incident {i+1}:")
            print(f"      ID: {incident[0]}")
            print(f"      Date début: {incident[1]}")
            print(f"      Heure début: {incident[2]}")
            print(f"      Résumé: {incident[3][:100]}..." if incident[3] else "      Résumé: None")
            print(f"      Entité: {incident[4]}")
            print(f"      État: {incident[5]}")
            print(f"      Type ID: {incident[6]}")
            print(f"      Source ID: {incident[7]}")
            print(f"      Entité ID: {incident[8]}")
            print(f"      Localisation ID: {incident[9]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Recréation terminée avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    recreate_tables_without_fk()
