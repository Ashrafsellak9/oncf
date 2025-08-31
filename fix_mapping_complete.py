#!/usr/bin/env python3
"""
Script complet pour corriger le mapping des données avec les vraies structures des tables
"""

import psycopg2
import os
import pandas as pd
from datetime import datetime

def fix_mapping_complete():
    """Corriger le mapping des données avec les vraies structures"""
    
    try:
        print("🔧 Correction complète du mapping des données")
        print("=" * 80)
        
        # Se connecter à la base de données
        print("\n🗄️ Connexion à la base de données...")
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
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
        
        # 2. Lire le fichier CSV des incidents
        print("\n📖 Lecture du fichier CSV incidents...")
        csv_file = "sql_data/incidents.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return False
        
        # Lire le CSV avec les bonnes colonnes (31 colonnes)
        df = pd.read_csv(csv_file, header=None)
        
        print(f"   {len(df)} incidents trouvés dans le CSV")
        
        # 3. Vider la table ge_evenement pour recommencer
        print("\n🗑️ Vidage de la table ge_evenement...")
        cursor.execute("DELETE FROM gpr.ge_evenement")
        cursor.execute("ALTER SEQUENCE gpr.ge_evenement_id_seq RESTART WITH 1")
        
        # 4. Insérer les données avec le bon mapping
        print("\n📝 Insertion des données avec le bon mapping...")
        
        for index, row in df.iterrows():
            try:
                # Mapping des colonnes selon la structure donnée
                incident_data = {
                    'date_avis': row[1] if pd.notna(row[1]) else None,
                    'date_debut': row[2] if pd.notna(row[2]) else None,
                    'date_fin': row[3] if pd.notna(row[3]) else None,
                    'date_impact': row[4] if pd.notna(row[4]) else None,
                    'datemaj': row[5] if pd.notna(row[5]) else None,
                    'entite': row[6] if pd.notna(row[6]) else None,
                    'etat': row[7] if pd.notna(row[7]) else None,
                    'heure_avis': row[8] if pd.notna(row[8]) else None,
                    'heure_debut': row[9] if pd.notna(row[9]) else None,
                    'heure_fin': row[10] if pd.notna(row[10]) else None,
                    'heure_impact': row[11] if pd.notna(row[11]) else None,
                    'impact_service': row[12] if pd.notna(row[12]) else None,
                    'important': row[13] if pd.notna(row[13]) else None,
                    'inclure_commentaire': row[14] if pd.notna(row[14]) else None,
                    'rapport_journalier': row[15] if pd.notna(row[15]) else None,
                    'resume': row[16] if pd.notna(row[16]) else None,
                    'source_personne': row[17] if pd.notna(row[17]) else None,
                    'user_id': row[18] if pd.notna(row[18]) else None,
                    'source_id': row[19] if pd.notna(row[19]) else None,
                    'sous_type_id': row[20] if pd.notna(row[20]) else None,
                    'system_id': row[21] if pd.notna(row[21]) else None,
                    'type_id': row[22] if pd.notna(row[22]) else None,
                    'extrait': row[23] if pd.notna(row[23]) else None,
                    'rapport_hebdomadaire': row[24] if pd.notna(row[24]) else None,
                    'fonction': row[25] if pd.notna(row[25]) else None,
                    'commentaire': row[26] if pd.notna(row[26]) else None,
                    'deleted': row[27] if pd.notna(row[27]) else False,
                    'responsabilite_id': row[28] if pd.notna(row[28]) else None,
                    'entite_id': row[29] if pd.notna(row[29]) else None,
                    'workflow_etape_id': row[30] if pd.notna(row[30]) else None
                }
                
                # Insérer l'incident
                cursor.execute("""
                    INSERT INTO gpr.ge_evenement (
                        date_avis, date_debut, date_fin, date_impact, datemaj,
                        entite, etat, heure_avis, heure_debut, heure_fin, heure_impact,
                        impact_service, important, inclure_commentaire, rapport_journalier,
                        resume, source_personne, user_id, source_id, sous_type_id,
                        system_id, type_id, extrait, rapport_hebdomadaire, fonction,
                        commentaire, deleted, responsabilite_id, entite_id, workflow_etape_id
                    ) VALUES (
                        %(date_avis)s, %(date_debut)s, %(date_fin)s, %(date_impact)s, %(datemaj)s,
                        %(entite)s, %(etat)s, %(heure_avis)s, %(heure_debut)s, %(heure_fin)s, %(heure_impact)s,
                        %(impact_service)s, %(important)s, %(inclure_commentaire)s, %(rapport_journalier)s,
                        %(resume)s, %(source_personne)s, %(user_id)s, %(source_id)s, %(sous_type_id)s,
                        %(system_id)s, %(type_id)s, %(extrait)s, %(rapport_hebdomadaire)s, %(fonction)s,
                        %(commentaire)s, %(deleted)s, %(responsabilite_id)s, %(entite_id)s, %(workflow_etape_id)s
                    )
                """, incident_data)
                
            except Exception as e:
                print(f"   ❌ Erreur ligne {index + 1}: {e}")
                continue
        
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
        
        # Valider les changements
        conn.commit()
        
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
        
        # 8. Vérifier les relations
        print("\n🔗 Vérification des relations...")
        
        # Vérifier les types
        cursor.execute("""
            SELECT COUNT(*) FROM gpr.ge_evenement e 
            LEFT JOIN gpr.ref_types t ON e.type_id = t.id 
            WHERE e.type_id IS NOT NULL AND t.id IS NULL
        """)
        invalid_types = cursor.fetchone()[0]
        print(f"   Type IDs invalides: {invalid_types}")
        
        # Vérifier les sources
        cursor.execute("""
            SELECT COUNT(*) FROM gpr.ge_evenement e 
            LEFT JOIN gpr.ref_sources s ON e.source_id = s.id 
            WHERE e.source_id IS NOT NULL AND s.id IS NULL
        """)
        invalid_sources = cursor.fetchone()[0]
        print(f"   Source IDs invalides: {invalid_sources}")
        
        # Vérifier les entités
        cursor.execute("""
            SELECT COUNT(*) FROM gpr.ge_evenement e 
            LEFT JOIN gpr.ref_entites ent ON e.entite_id = ent.id 
            WHERE e.entite_id IS NOT NULL AND ent.id IS NULL
        """)
        invalid_entites = cursor.fetchone()[0]
        print(f"   Entité IDs invalides: {invalid_entites}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Correction terminée avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    fix_mapping_complete()
