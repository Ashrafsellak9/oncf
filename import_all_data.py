import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime
import re

# Configuration de la base de données
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/oncf_achraf"

def create_database():
    """Créer la base de données si elle n'existe pas"""
    try:
        # Connexion à postgres pour créer la base de données
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/postgres")
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Vérifier si la base de données existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'oncf_achraf'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE oncf_achraf")
            print("Base de données 'oncf_achraf' créée avec succès")
        else:
            print("Base de données 'oncf_achraf' existe déjà")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur lors de la création de la base de données: {e}")

def create_schema_and_tables():
    """Créer le schéma et les tables"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Créer le schéma gpr
    cursor.execute("CREATE SCHEMA IF NOT EXISTS gpr")
    
    # Table axes (graphe_arc)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.graphe_arc (
            id SERIAL PRIMARY KEY,
            axe VARCHAR(255),
            cumuld NUMERIC,
            cumulf NUMERIC,
            plod VARCHAR(255),
            absd NUMERIC,
            plof VARCHAR(255),
            absf NUMERIC,
            geometrie TEXT
        )
    """)
    
    # Table gares (gpd_gares_ref)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.gpd_gares_ref (
            id SERIAL PRIMARY KEY,
            axe VARCHAR(255),
            plod VARCHAR(255),
            absd VARCHAR(255),
            geometrie TEXT,
            geometrie_dec TEXT,
            codegare VARCHAR(255),
            codeoperationnel VARCHAR(255),
            codereseau VARCHAR(255),
            nomgarefr VARCHAR(255),
            typegare VARCHAR(255),
            publishid VARCHAR(255),
            sivtypegare VARCHAR(255),
            num_pk VARCHAR(255),
            idville INTEGER,
            villes_ville VARCHAR(255),
            etat VARCHAR(255)
        )
    """)
    
    # Table incidents (ge_evenement)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.ge_evenement (
            id SERIAL PRIMARY KEY,
            date_avis TIMESTAMP,
            date_debut TIMESTAMP,
            date_fin TIMESTAMP,
            date_impact TIMESTAMP,
            heure_avis TIME,
            heure_debut TIME,
            heure_fin TIME,
            heure_impact TIME,
            resume TEXT,
            commentaire TEXT,
            extrait TEXT,
            etat VARCHAR(255),
            type_id INTEGER,
            sous_type_id INTEGER,
            source_id INTEGER,
            user_id INTEGER,
            important BOOLEAN,
            impact_service BOOLEAN
        )
    """)
    
    # Table localisation (ge_localisation)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.ge_localisation (
            id SERIAL PRIMARY KEY,
            autre VARCHAR(255),
            commentaire TEXT,
            type_localisation VARCHAR(255),
            type_pk VARCHAR(255),
            pk_debut VARCHAR(255),
            pk_fin VARCHAR(255),
            gare_debut_id VARCHAR(255),
            gare_fin_id VARCHAR(255),
            evenement_id INTEGER,
            user_id INTEGER
        )
    """)
    
    # Table ref_types
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.ref_types (
            id SERIAL PRIMARY KEY,
            date_maj TIMESTAMP,
            intitule VARCHAR(255),
            entite_type_id INTEGER,
            etat BOOLEAN,
            deleted BOOLEAN
        )
    """)
    
    # Table ref_sous_types
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.ref_sous_types (
            id SERIAL PRIMARY KEY,
            date_maj TIMESTAMP,
            intitule VARCHAR(255),
            type_id INTEGER,
            etat BOOLEAN,
            deleted BOOLEAN
        )
    """)
    
    # Table ref_systemes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.ref_systemes (
            id SERIAL PRIMARY KEY,
            date_maj TIMESTAMP,
            intitule VARCHAR(255),
            entite_type_id INTEGER,
            etat BOOLEAN,
            deleted BOOLEAN
        )
    """)
    
    # Table ref_sources
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.ref_sources (
            id SERIAL PRIMARY KEY,
            date_maj TIMESTAMP,
            intitule VARCHAR(255),
            entite_type_id INTEGER,
            etat BOOLEAN,
            deleted BOOLEAN
        )
    """)
    
    # Table ref_entites
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.ref_entites (
            id SERIAL PRIMARY KEY,
            date_maj TIMESTAMP,
            intitule VARCHAR(255),
            etat BOOLEAN,
            deleted BOOLEAN
        )
    """)
    
    # Table users pour l'authentification
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpr.users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            role VARCHAR(20) DEFAULT 'user',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Schéma et tables créés avec succès")

def parse_geometry(geom_str):
    """Parser une géométrie WKT ou WKB"""
    if not geom_str or geom_str == '':
        return None
    
    # Si c'est déjà au format WKT, le retourner tel quel
    if geom_str.startswith('SRID=') or geom_str.startswith('POINT') or geom_str.startswith('LINESTRING'):
        return geom_str
    
    # Si c'est du WKB hexadécimal, le convertir en WKT
    try:
        if len(geom_str) > 18:
            # Format WKB avec SRID
            if geom_str.startswith('0101000020'):
                # Point avec SRID
                coords_hex = geom_str[18:]
                if len(coords_hex) >= 16:
                    x_hex = coords_hex[:16]
                    y_hex = coords_hex[16:32]
                    
                    # Convertir hex en float (little endian)
                    x_bytes = bytes.fromhex(x_hex)
                    y_bytes = bytes.fromhex(y_hex)
                    
                    import struct
                    x = struct.unpack('<d', x_bytes)[0]
                    y = struct.unpack('<d', y_bytes)[0]
                    
                    return f"SRID=3857;POINT({x} {y})"
    except:
        pass
    
    return geom_str

def import_axes_data():
    """Importer les données des axes"""
    print("Importation des données des axes...")
    
    # Lire le fichier CSV par chunks pour gérer la mémoire
    chunk_size = 1000
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Vider la table d'abord
    cursor.execute("DELETE FROM gpr.graphe_arc")
    
    for chunk in pd.read_csv('sql_data/axes.csv', chunksize=chunk_size, header=None):
        data = []
        for _, row in chunk.iterrows():
            try:
                # Parser les données selon la structure observée
                axe = str(row[1]) if len(row) > 1 else None
                cumuld = float(row[2]) if len(row) > 2 and pd.notna(row[2]) else None
                cumulf = float(row[3]) if len(row) > 3 and pd.notna(row[3]) else None
                plod = str(row[4]) if len(row) > 4 else None
                absd = float(row[5]) if len(row) > 5 and pd.notna(row[5]) else None
                plof = str(row[6]) if len(row) > 6 else None
                absf = float(row[7]) if len(row) > 7 and pd.notna(row[7]) else None
                geometrie = parse_geometry(str(row[8])) if len(row) > 8 else None
                
                data.append((axe, cumuld, cumulf, plod, absd, plof, absf, geometrie))
            except Exception as e:
                print(f"Erreur lors du parsing de la ligne: {e}")
                continue
        
        if data:
            execute_values(cursor, """
                INSERT INTO gpr.graphe_arc (axe, cumuld, cumulf, plod, absd, plof, absf, geometrie)
                VALUES %s
            """, data)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Données des axes importées avec succès")

def import_gares_data():
    """Importer les données des gares"""
    print("Importation des données des gares...")
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Vider la table d'abord
    cursor.execute("DELETE FROM gpr.gpd_gares_ref")
    
    df = pd.read_csv('sql_data/gares.csv', header=None)
    data = []
    
    for _, row in df.iterrows():
        try:
            axe = str(row[1]) if len(row) > 1 else None
            plod = str(row[2]) if len(row) > 2 else None
            absd = str(row[3]) if len(row) > 3 else None
            geometrie = parse_geometry(str(row[4])) if len(row) > 4 else None
            geometrie_dec = parse_geometry(str(row[5])) if len(row) > 5 else None
            codegare = str(row[6]) if len(row) > 6 else None
            codeoperationnel = str(row[7]) if len(row) > 7 else None
            codereseau = str(row[8]) if len(row) > 8 else None
            nomgarefr = str(row[9]) if len(row) > 9 else None
            typegare = str(row[10]) if len(row) > 10 else None
            publishid = str(row[11]) if len(row) > 11 else None
            sivtypegare = str(row[12]) if len(row) > 12 else None
            num_pk = str(row[13]) if len(row) > 13 else None
            idville = int(row[14]) if len(row) > 14 and pd.notna(row[14]) else None
            villes_ville = str(row[15]) if len(row) > 15 else None
            etat = str(row[16]) if len(row) > 16 else None
            
            data.append((axe, plod, absd, geometrie, geometrie_dec, codegare, 
                        codeoperationnel, codereseau, nomgarefr, typegare, 
                        publishid, sivtypegare, num_pk, idville, villes_ville, etat))
        except Exception as e:
            print(f"Erreur lors du parsing de la ligne gare: {e}")
            continue
    
    if data:
        execute_values(cursor, """
            INSERT INTO gpr.gpd_gares_ref (axe, plod, absd, geometrie, geometrie_dec, 
            codegare, codeoperationnel, codereseau, nomgarefr, typegare, 
            publishid, sivtypegare, num_pk, idville, villes_ville, etat)
            VALUES %s
        """, data)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Données des gares importées avec succès")

def import_incidents_data():
    """Importer les données des incidents"""
    print("Importation des données des incidents...")
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Vider la table d'abord
    cursor.execute("DELETE FROM gpr.ge_evenement")
    
    df = pd.read_csv('sql_data/incidents.csv', header=None)
    data = []
    
    for _, row in df.iterrows():
        try:
            # Parser les dates et heures
            date_avis = pd.to_datetime(row[1]) if len(row) > 1 and pd.notna(row[1]) else None
            date_debut = pd.to_datetime(row[2]) if len(row) > 2 and pd.notna(row[2]) else None
            date_fin = pd.to_datetime(row[3]) if len(row) > 3 and pd.notna(row[3]) else None
            date_impact = pd.to_datetime(row[4]) if len(row) > 4 and pd.notna(row[4]) else None
            
            # Parser les heures
            heure_avis = str(row[8]) if len(row) > 8 and pd.notna(row[8]) else None
            heure_debut = str(row[9]) if len(row) > 9 and pd.notna(row[9]) else None
            heure_fin = str(row[10]) if len(row) > 10 and pd.notna(row[10]) else None
            heure_impact = str(row[11]) if len(row) > 11 and pd.notna(row[11]) else None
            
            resume = str(row[12]) if len(row) > 12 else None
            commentaire = str(row[13]) if len(row) > 13 else None
            extrait = str(row[14]) if len(row) > 14 else None
            etat = str(row[15]) if len(row) > 15 else None
            
            # Parser les IDs
            type_id = int(row[16]) if len(row) > 16 and pd.notna(row[16]) else None
            sous_type_id = int(row[17]) if len(row) > 17 and pd.notna(row[17]) else None
            source_id = int(row[18]) if len(row) > 18 and pd.notna(row[18]) else None
            user_id = int(row[19]) if len(row) > 19 and pd.notna(row[19]) else None
            
            # Parser les booléens
            important = str(row[20]).lower() == 't' if len(row) > 20 else False
            impact_service = str(row[21]).lower() == 't' if len(row) > 21 else False
            
            data.append((date_avis, date_debut, date_fin, date_impact, heure_avis, 
                        heure_debut, heure_fin, heure_impact, resume, commentaire, 
                        extrait, etat, type_id, sous_type_id, source_id, user_id, 
                        important, impact_service))
        except Exception as e:
            print(f"Erreur lors du parsing de la ligne incident: {e}")
            continue
    
    if data:
        execute_values(cursor, """
            INSERT INTO gpr.ge_evenement (date_avis, date_debut, date_fin, date_impact,
            heure_avis, heure_debut, heure_fin, heure_impact, resume, commentaire,
            extrait, etat, type_id, sous_type_id, source_id, user_id, important, impact_service)
            VALUES %s
        """, data)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Données des incidents importées avec succès")

def import_localisation_data():
    """Importer les données de localisation"""
    print("Importation des données de localisation...")
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Vider la table d'abord
    cursor.execute("DELETE FROM gpr.ge_localisation")
    
    df = pd.read_csv('sql_data/localisation.csv', header=None)
    data = []
    
    for _, row in df.iterrows():
        try:
            autre = str(row[1]) if len(row) > 1 else None
            commentaire = str(row[2]) if len(row) > 2 else None
            type_localisation = str(row[4]) if len(row) > 4 else None
            type_pk = str(row[5]) if len(row) > 5 else None
            pk_debut = str(row[6]) if len(row) > 6 else None
            pk_fin = str(row[7]) if len(row) > 7 else None
            gare_debut_id = str(row[8]) if len(row) > 8 else None
            gare_fin_id = str(row[9]) if len(row) > 9 else None
            evenement_id = int(row[10]) if len(row) > 10 and pd.notna(row[10]) else None
            user_id = int(row[11]) if len(row) > 11 and pd.notna(row[11]) else None
            
            data.append((autre, commentaire, type_localisation, type_pk, pk_debut, 
                        pk_fin, gare_debut_id, gare_fin_id, evenement_id, user_id))
        except Exception as e:
            print(f"Erreur lors du parsing de la ligne localisation: {e}")
            continue
    
    if data:
        execute_values(cursor, """
            INSERT INTO gpr.ge_localisation (autre, commentaire, type_localisation, type_pk,
            pk_debut, pk_fin, gare_debut_id, gare_fin_id, evenement_id, user_id)
            VALUES %s
        """, data)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Données de localisation importées avec succès")

def import_reference_data():
    """Importer les données de référence"""
    print("Importation des données de référence...")
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Importer ref_types
    if os.path.exists('sql_data/ref_types.csv'):
        cursor.execute("DELETE FROM gpr.ref_types")
        df = pd.read_csv('sql_data/ref_types.csv', header=None)
        data = []
        for _, row in df.iterrows():
            try:
                date_maj = pd.to_datetime(row[1]) if len(row) > 1 and pd.notna(row[1]) else None
                intitule = str(row[2]) if len(row) > 2 else None
                entite_type_id = int(row[3]) if len(row) > 3 and pd.notna(row[3]) else None
                etat = str(row[4]).lower() == 't' if len(row) > 4 else True
                deleted = str(row[5]).lower() == 't' if len(row) > 5 else False
                data.append((date_maj, intitule, entite_type_id, etat, deleted))
            except Exception as e:
                print(f"Erreur ref_types: {e}")
                continue
        
        if data:
            execute_values(cursor, """
                INSERT INTO gpr.ref_types (date_maj, intitule, entite_type_id, etat, deleted)
                VALUES %s
            """, data)
    
    # Importer ref_sous_types
    if os.path.exists('sql_data/ref_sous_types.csv'):
        cursor.execute("DELETE FROM gpr.ref_sous_types")
        df = pd.read_csv('sql_data/ref_sous_types.csv', header=None)
        data = []
        for _, row in df.iterrows():
            try:
                date_maj = pd.to_datetime(row[1]) if len(row) > 1 and pd.notna(row[1]) else None
                intitule = str(row[2]) if len(row) > 2 else None
                type_id = int(row[3]) if len(row) > 3 and pd.notna(row[3]) else None
                etat = str(row[4]).lower() == 't' if len(row) > 4 else True
                deleted = str(row[5]).lower() == 't' if len(row) > 5 else False
                data.append((date_maj, intitule, type_id, etat, deleted))
            except Exception as e:
                print(f"Erreur ref_sous_types: {e}")
                continue
        
        if data:
            execute_values(cursor, """
                INSERT INTO gpr.ref_sous_types (date_maj, intitule, type_id, etat, deleted)
                VALUES %s
            """, data)
    
    # Importer ref_systemes
    if os.path.exists('sql_data/ref_systemes.csv'):
        cursor.execute("DELETE FROM gpr.ref_systemes")
        df = pd.read_csv('sql_data/ref_systemes.csv', header=None)
        data = []
        for _, row in df.iterrows():
            try:
                date_maj = pd.to_datetime(row[1]) if len(row) > 1 and pd.notna(row[1]) else None
                intitule = str(row[2]) if len(row) > 2 else None
                entite_type_id = int(row[3]) if len(row) > 3 and pd.notna(row[3]) else None
                etat = str(row[4]).lower() == 't' if len(row) > 4 else True
                deleted = str(row[5]).lower() == 't' if len(row) > 5 else False
                data.append((date_maj, intitule, entite_type_id, etat, deleted))
            except Exception as e:
                print(f"Erreur ref_systemes: {e}")
                continue
        
        if data:
            execute_values(cursor, """
                INSERT INTO gpr.ref_systemes (date_maj, intitule, entite_type_id, etat, deleted)
                VALUES %s
            """, data)
    
    # Importer ref_sources
    if os.path.exists('sql_data/ref_sources.csv'):
        cursor.execute("DELETE FROM gpr.ref_sources")
        df = pd.read_csv('sql_data/ref_sources.csv', header=None)
        data = []
        for _, row in df.iterrows():
            try:
                date_maj = pd.to_datetime(row[1]) if len(row) > 1 and pd.notna(row[1]) else None
                intitule = str(row[2]) if len(row) > 2 else None
                entite_type_id = int(row[3]) if len(row) > 3 and pd.notna(row[3]) else None
                etat = str(row[4]).lower() == 't' if len(row) > 4 else True
                deleted = str(row[5]).lower() == 't' if len(row) > 5 else False
                data.append((date_maj, intitule, entite_type_id, etat, deleted))
            except Exception as e:
                print(f"Erreur ref_sources: {e}")
                continue
        
        if data:
            execute_values(cursor, """
                INSERT INTO gpr.ref_sources (date_maj, intitule, entite_type_id, etat, deleted)
                VALUES %s
            """, data)
    
    # Importer ref_entites
    if os.path.exists('sql_data/ref_entites.csv'):
        cursor.execute("DELETE FROM gpr.ref_entites")
        df = pd.read_csv('sql_data/ref_entites.csv', header=None)
        data = []
        for _, row in df.iterrows():
            try:
                date_maj = pd.to_datetime(row[1]) if len(row) > 1 and pd.notna(row[1]) else None
                intitule = str(row[2]) if len(row) > 2 else None
                etat = str(row[3]).lower() == 't' if len(row) > 3 else True
                deleted = str(row[4]).lower() == 't' if len(row) > 4 else False
                data.append((date_maj, intitule, etat, deleted))
            except Exception as e:
                print(f"Erreur ref_entites: {e}")
                continue
        
        if data:
            execute_values(cursor, """
                INSERT INTO gpr.ref_entites (date_maj, intitule, etat, deleted)
                VALUES %s
            """, data)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Données de référence importées avec succès")

def main():
    """Fonction principale d'importation"""
    print("Début de l'importation des données...")
    
    # Créer la base de données
    create_database()
    
    # Créer le schéma et les tables
    create_schema_and_tables()
    
    # Importer toutes les données
    import_axes_data()
    import_gares_data()
    import_incidents_data()
    import_localisation_data()
    import_reference_data()
    
    print("Importation terminée avec succès!")

if __name__ == "__main__":
    main()
