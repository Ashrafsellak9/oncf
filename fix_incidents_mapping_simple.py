#!/usr/bin/env python3
"""
Script simple pour corriger le mapping des données dans la table ge_evenement
"""

import psycopg2
import os

def fix_incidents_mapping_simple():
    """Corriger le mapping des données dans la table ge_evenement avec SQL direct"""
    
    try:
        print("🔧 Correction simple du mapping des données dans ge_evenement")
        print("=" * 80)
        
        # Se connecter à la base de données
        print("\n🗄️ Connexion à la base de données...")
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        # 1. Corriger le mapping des colonnes avec SQL direct
        print("\n📝 Correction du mapping des colonnes...")
        
        # Échanger description et axe
        cursor.execute("""
            UPDATE gpr.ge_evenement 
            SET description = axe, axe = description 
            WHERE description ~ '^[0-9]{1,2}:[0-9]{2}:[0-9]{2}$'
        """)
        
        print(f"   {cursor.rowcount} lignes mises à jour (description <-> axe)")
        
        # Corriger le résumé
        cursor.execute("""
            UPDATE gpr.ge_evenement 
            SET resume = description 
            WHERE resume ~ '^[0-9]{1,2}:[0-9]{2}:[0-9]{2}$'
        """)
        
        print(f"   {cursor.rowcount} lignes mises à jour (resume)")
        
        # Corriger les IDs des références
        print("\n🔗 Correction des IDs de référence...")
        
        # Mettre à jour les source_id basés sur les valeurs dans la colonne axe
        cursor.execute("""
            UPDATE gpr.ge_evenement 
            SET source_id = CASE 
                WHEN axe LIKE '%ADS%' THEN 1
                WHEN axe LIKE '%PF%' THEN 2
                WHEN axe LIKE '%CNC%' THEN 3
                WHEN axe LIKE '%Chef site%' THEN 4
                WHEN axe LIKE '%Assistant clientèle%' THEN 5
                WHEN axe LIKE '%R.Caténaire%' THEN 6
                ELSE source_id
            END
        """)
        
        print(f"   {cursor.rowcount} lignes mises à jour (source_id)")
        
        # Mettre à jour les type_id basés sur le contenu
        cursor.execute("""
            UPDATE gpr.ge_evenement 
            SET type_id = CASE 
                WHEN axe LIKE '%jet de pierre%' THEN 1
                WHEN axe LIKE '%signal d''alarme%' THEN 2
                WHEN axe LIKE '%vol%' THEN 3
                WHEN axe LIKE '%tamponnement%' THEN 4
                WHEN axe LIKE '%arrêt%' THEN 5
                WHEN axe LIKE '%défaut%' THEN 6
                ELSE type_id
            END
        """)
        
        print(f"   {cursor.rowcount} lignes mises à jour (type_id)")
        
        # Corriger les localisations
        print("\n📍 Correction des localisations...")
        
        # Créer des localisations basées sur les gares
        cursor.execute("""
            INSERT INTO gpr.ge_localisation (evenement_id, gare_debut_id, type_localisation)
            SELECT e.id, e.gare, 'gare'
            FROM gpr.ge_evenement e
            WHERE e.gare IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM gpr.ge_localisation l WHERE l.evenement_id = e.id
            )
        """)
        
        print(f"   {cursor.rowcount} localisations créées")
        
        # Mettre à jour les localisation_id
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
        
        # Vérifier le résultat
        print("\n✅ Vérification du résultat...")
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_evenement")
        total = cursor.fetchone()[0]
        print(f"   Total incidents: {total}")
        
        # Vérifier quelques exemples
        cursor.execute("""
            SELECT id, date_debut, heure_debut, description, axe, section, gare, type_id, source_id, localisation_id
            FROM gpr.ge_evenement 
            LIMIT 3
        """)
        
        incidents = cursor.fetchall()
        for i, incident in enumerate(incidents):
            print(f"\n   Incident {i+1}:")
            print(f"      ID: {incident[0]}")
            print(f"      Date début: {incident[1]}")
            print(f"      Heure début: {incident[2]}")
            print(f"      Description: {incident[3][:100]}..." if incident[3] else "      Description: None")
            print(f"      Axe: {incident[4][:50]}..." if incident[4] else "      Axe: None")
            print(f"      Section: {incident[5]}")
            print(f"      Gare: {incident[6]}")
            print(f"      Type ID: {incident[7]}")
            print(f"      Source ID: {incident[8]}")
            print(f"      Localisation ID: {incident[9]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Correction terminée avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    fix_incidents_mapping_simple()
