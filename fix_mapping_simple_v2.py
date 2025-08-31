#!/usr/bin/env python3
"""
Script simple et robuste pour corriger le mapping des données
"""

import psycopg2
import os
import pandas as pd

def fix_mapping_simple_v2():
    """Corriger le mapping des données de manière simple et robuste"""
    
    try:
        print("🔧 Correction simple du mapping des données")
        print("=" * 60)
        
        # Se connecter à la base de données
        print("\n🗄️ Connexion à la base de données...")
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        conn.autocommit = True  # Éviter les problèmes de transaction
        cursor = conn.cursor()
        
        # 1. Créer la table ref_site_surete si elle n'existe pas
        print("\n🏢 Création de la table ref_site_surete...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpr.ref_site_surete (
                id SERIAL PRIMARY KEY,
                intitule VARCHAR(255) NOT NULL
            )
        """)
        
        # Insérer les données de ref_site_surete
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
                ON CONFLICT (id) DO UPDATE SET intitule = EXCLUDED.intitule
            """, (site_id, intitule))
        
        print(f"   {len(sites_surete)} sites de sûreté insérés/mis à jour")
        
        # 2. Vider la table ge_evenement
        print("\n🗑️ Vidage de la table ge_evenement...")
        cursor.execute("DELETE FROM gpr.ge_evenement")
        cursor.execute("ALTER SEQUENCE gpr.ge_evenement_id_seq RESTART WITH 1")
        
        # 3. Lire le fichier CSV des incidents
        print("\n📖 Lecture du fichier CSV incidents...")
        csv_file = "sql_data/incidents.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return False
        
        # Lire le CSV avec les bonnes colonnes (31 colonnes)
        df = pd.read_csv(csv_file, header=None)
        
        print(f"   {len(df)} incidents trouvés dans le CSV")
        
        # 4. Insérer les données avec le bon mapping (ligne par ligne)
        print("\n📝 Insertion des données avec le bon mapping...")
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Mapping des colonnes selon la structure donnée
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
                    row[1] if pd.notna(row[1]) else None,
                    row[2] if pd.notna(row[2]) else None,
                    row[3] if pd.notna(row[3]) else None,
                    row[4] if pd.notna(row[4]) else None,
                    row[5] if pd.notna(row[5]) else None,
                    row[6] if pd.notna(row[6]) else None,
                    row[7] if pd.notna(row[7]) else None,
                    row[8] if pd.notna(row[8]) else None,
                    row[9] if pd.notna(row[9]) else None,
                    row[10] if pd.notna(row[10]) else None,
                    row[11] if pd.notna(row[11]) else None,
                    row[12] if pd.notna(row[12]) else None,
                    row[13] if pd.notna(row[13]) else None,
                    row[14] if pd.notna(row[14]) else None,
                    row[15] if pd.notna(row[15]) else None,
                    row[16] if pd.notna(row[16]) else None,
                    row[17] if pd.notna(row[17]) else None,
                    row[18] if pd.notna(row[18]) else None,
                    row[19] if pd.notna(row[19]) else None,
                    row[20] if pd.notna(row[20]) else None,
                    row[21] if pd.notna(row[21]) else None,
                    row[22] if pd.notna(row[22]) else None,
                    row[23] if pd.notna(row[23]) else None,
                    row[24] if pd.notna(row[24]) else None,
                    row[25] if pd.notna(row[25]) else None,
                    row[26] if pd.notna(row[26]) else None,
                    row[27] if pd.notna(row[27]) else False,
                    row[28] if pd.notna(row[28]) else None,
                    row[29] if pd.notna(row[29]) else None,
                    row[30] if pd.notna(row[30]) else None
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
        
        # 5. Créer les localisations pour chaque incident
        print("\n📍 Création des localisations...")
        cursor.execute("""
            INSERT INTO gpr.ge_localisation (
                evenement_id, type_localisation, datemaj, user_id
            )
            SELECT 
                id, 
                'incident' as type_localisation,
                NOW() as datemaj,
                1 as user_id
            FROM gpr.ge_evenement
            WHERE id NOT IN (SELECT evenement_id FROM gpr.ge_localisation WHERE evenement_id IS NOT NULL)
        """)
        
        print(f"   {cursor.rowcount} localisations créées")
        
        # 6. Mettre à jour les localisation_id dans ge_evenement
        print("\n🔗 Mise à jour des localisation_id...")
        cursor.execute("""
            UPDATE gpr.ge_evenement e
            SET localisation_id = l.id
            FROM gpr.ge_localisation l
            WHERE l.evenement_id = e.id
            AND e.localisation_id IS NULL
        """)
        
        print(f"   {cursor.rowcount} localisation_id mis à jour")
        
        # 7. Vérifier le résultat
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
        
        print("\n🎉 Correction terminée avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    fix_mapping_simple_v2()
