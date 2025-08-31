#!/usr/bin/env python3
"""
Import simple des incidents un par un
"""

import pandas as pd
import psycopg2

def safe_int(value):
    """Convertir en int de manière sécurisée"""
    if pd.isna(value) or value == '' or value == 'f' or value == 't':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def safe_float(value):
    """Convertir en float de manière sécurisée"""
    if pd.isna(value) or value == '' or value == 'f' or value == 't':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_str(value):
    """Convertir en string de manière sécurisée"""
    if pd.isna(value) or value == '':
        return None
    return str(value)

def import_incidents_simple_final():
    """Import simple des incidents un par un"""
    try:
        # Connexion
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres",
            port="5432"
        )
        
        # Lire le CSV
        csv_file = "sql_data/incidents.csv"
        df = pd.read_csv(csv_file, header=None)
        print(f"📖 {len(df)} incidents trouvés")
        
        # Insérer les données un par un
        inserted_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Créer une nouvelle connexion pour chaque incident
                incident_conn = psycopg2.connect(
                    host="localhost",
                    database="oncf_achraf",
                    user="postgres",
                    password="postgres",
                    port="5432"
                )
                cursor = incident_conn.cursor()
                
                # Extraire les données
                gid = safe_int(row[0])
                date_debut = pd.to_datetime(row[1]) if pd.notna(row[1]) else None
                date_fin = pd.to_datetime(row[2]) if pd.notna(row[2]) else None
                date_creation = pd.to_datetime(row[5]) if pd.notna(row[5]) else None
                type_id = safe_int(row[6])
                statut = safe_str(row[7])
                description = safe_str(row[8])
                resume = safe_str(row[9])
                localisation_id = safe_int(row[10])
                source_id = safe_int(row[11])
                sous_type_id = safe_int(row[12])
                systeme_id = safe_int(row[13])
                entite_id = safe_int(row[14])
                site_surete_id = safe_int(row[15])
                axe = safe_str(row[16])
                section = safe_str(row[17])
                gare = safe_str(row[18])
                pk_debut = safe_float(row[19])
                pk_fin = safe_float(row[20])
                
                # Chercher les heures
                heure_debut = None
                heure_fin = None
                for col_idx in [8, 9, 3, 4]:
                    if col_idx < len(row) and pd.notna(row[col_idx]):
                        val = str(row[col_idx])
                        if ':' in val and len(val) <= 8:
                            if heure_debut is None:
                                heure_debut = val
                            elif heure_fin is None:
                                heure_fin = val
                                break
                
                # Insérer
                insert_sql = """
                INSERT INTO ge_evenement (
                    gid, date_debut, date_fin, heure_debut, heure_fin, date_creation, 
                    type_id, statut, description, resume, localisation_id, source_id, 
                    sous_type_id, systeme_id, entite_id, site_surete_id, axe, section, 
                    gare, pk_debut, pk_fin
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                
                cursor.execute(insert_sql, (
                    gid, date_debut, date_fin, heure_debut, heure_fin, date_creation,
                    type_id, statut, description, resume, localisation_id, source_id,
                    sous_type_id, systeme_id, entite_id, site_surete_id, axe, section,
                    gare, pk_debut, pk_fin
                ))
                
                incident_conn.commit()
                inserted_count += 1
                
                if inserted_count % 10 == 0:
                    print(f"📊 {inserted_count} incidents importés...")
                
                incident_conn.close()
                    
            except Exception as e:
                error_count += 1
                print(f"⚠️ Erreur incident {index + 1}: {e}")
                if 'incident_conn' in locals():
                    incident_conn.close()
                continue
        
        print(f"✅ {inserted_count} incidents importés avec succès!")
        print(f"❌ {error_count} erreurs")
        
        # Vérifier
        final_conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres",
            port="5432"
        )
        cursor = final_conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ge_evenement;")
        count = cursor.fetchone()[0]
        print(f"📊 Total dans la base: {count}")
        
        # Statistiques
        cursor.execute("SELECT statut, COUNT(*) FROM ge_evenement GROUP BY statut;")
        stats = cursor.fetchall()
        print("\n📈 Par statut:")
        for statut, count in stats:
            print(f"   {statut}: {count}")
        
        # Types d'incidents
        cursor.execute("SELECT type_id, COUNT(*) FROM ge_evenement GROUP BY type_id ORDER BY COUNT(*) DESC LIMIT 5;")
        types = cursor.fetchall()
        print("\n📊 Top 5 types d'incidents:")
        for type_id, count in types:
            print(f"   Type {type_id}: {count}")
        
        final_conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import_incidents_simple_final()
