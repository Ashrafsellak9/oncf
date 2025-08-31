#!/usr/bin/env python3
"""
Script pour corriger le mapping des données dans la table ge_evenement
"""

import psycopg2
import os
import pandas as pd
from datetime import datetime

def fix_incidents_mapping():
    """Corriger le mapping des données dans la table ge_evenement"""
    
    try:
        print("🔧 Correction du mapping des données dans ge_evenement")
        print("=" * 80)
        
        # 1. Lire le fichier CSV original
        print("\n📖 Lecture du fichier CSV original...")
        csv_file = "sql_data/incidents.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return False
        
        # Lire le CSV avec les bonnes colonnes (31 colonnes)
        df = pd.read_csv(csv_file, header=None)
        
        # Définir les noms de colonnes basés sur la structure observée
        columns = [
            'gid', 'date_debut', 'date_fin', 'date_impact', 'heure_impact', 'date_creation', 
            'type_id', 'statut', 'heure_debut', 'heure_fin', 'heure_impact_2', 'heure_impact_3',
            'flag1', 'flag2', 'flag3', 'flag4', 'description', 'section', 'gare', 'sous_type_id',
            'source_id', 'systeme_id', 'entite_id', 'site_surete_id', 'flag5', 'source_name',
            'col26', 'col27', 'col28', 'col29', 'col30'
        ]
        
        df.columns = columns
        
        print(f"✅ CSV lu avec {len(df)} lignes")
        print(f"   Colonnes: {len(df.columns)}")
        
        # 2. Se connecter à la base de données
        print("\n🗄️ Connexion à la base de données...")
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        # 3. Vider la table existante
        print("\n🗑️ Vidage de la table ge_evenement...")
        cursor.execute("DELETE FROM gpr.ge_evenement")
        print(f"   {cursor.rowcount} lignes supprimées")
        
        # 4. Réimporter les données avec le bon mapping
        print("\n📥 Réimport des données avec le bon mapping...")
        
        for index, row in df.iterrows():
            try:
                # Convertir les dates
                date_debut = None
                date_fin = None
                date_impact = None
                date_creation = None
                
                if pd.notna(row['date_debut']):
                    date_debut = pd.to_datetime(row['date_debut'])
                if pd.notna(row['date_fin']):
                    date_fin = pd.to_datetime(row['date_fin'])
                if pd.notna(row['date_impact']):
                    date_impact = pd.to_datetime(row['date_impact'])
                if pd.notna(row['date_creation']):
                    date_creation = pd.to_datetime(row['date_creation'])
                
                # Convertir les heures
                heure_debut = None
                heure_fin = None
                heure_impact = None
                
                if pd.notna(row['heure_debut']):
                    heure_debut = str(row['heure_debut'])
                if pd.notna(row['heure_fin']):
                    heure_fin = str(row['heure_fin'])
                if pd.notna(row['heure_impact']):
                    heure_impact = str(row['heure_impact'])
                
                # Insérer avec le bon mapping
                cursor.execute("""
                    INSERT INTO gpr.ge_evenement (
                        gid, date_debut, date_fin, date_impact, date_creation,
                        type_id, statut, heure_debut, heure_fin, heure_impact,
                        description, resume, localisation_id, source_id, sous_type_id,
                        systeme_id, entite_id, site_surete_id, axe, section, gare,
                        pk_debut, pk_fin, geometrie, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    row['gid'], date_debut, date_fin, date_impact, date_creation,
                    row['type_id'], row['statut'], heure_debut, heure_fin, heure_impact,
                    row['description'], row['description'], None,  # resume = description, localisation_id = None
                    row['source_id'], row['sous_type_id'], row['systeme_id'], 
                    row['entite_id'], row['site_surete_id'], row['source_name'], row['section'], 
                    row['gare'], None, None, None,  # pk_debut, pk_fin, geometrie = None
                    date_creation, date_creation
                ))
                
            except Exception as e:
                print(f"   ❌ Erreur ligne {index}: {e}")
                continue
        
        # 5. Valider les changements
        conn.commit()
        
        # 6. Vérifier le résultat
        print("\n✅ Vérification du résultat...")
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_evenement")
        total = cursor.fetchone()[0]
        print(f"   Total incidents: {total}")
        
        # Vérifier quelques exemples
        cursor.execute("""
            SELECT id, date_debut, heure_debut, description, axe, section, gare, type_id, source_id
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
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Correction terminée avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    fix_incidents_mapping()
