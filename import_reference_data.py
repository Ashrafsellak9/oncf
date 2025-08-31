#!/usr/bin/env python3
"""
Script pour importer les données des tables de référence
"""

import psycopg2
import os
import pandas as pd

def import_reference_data():
    """Importer les données des tables de référence"""
    
    try:
        print("📝 Import des données des tables de référence")
        print("=" * 80)
        
        # Se connecter à la base de données
        print("\n🗄️ Connexion à la base de données...")
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 1. Importer ref_entites
        print("\n🏢 Import de ref_entites...")
        csv_file = "sql_data/ref_entites.csv"
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file, header=None)
            print(f"   {len(df)} entités trouvées dans le CSV")
            
            for index, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO gpr.ref_entites (id, intitule) 
                        VALUES (%s, %s)
                    """, (row[0], row[1]))
                except Exception as e:
                    print(f"   ⚠️  Erreur ligne {index + 1}: {e}")
            
            print(f"   ✅ {len(df)} entités importées")
        else:
            print(f"   ❌ Fichier {csv_file} non trouvé")
        
        # 2. Importer ref_systemes
        print("\n🏢 Import de ref_systemes...")
        csv_file = "sql_data/ref_systemes.csv"
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file, header=None)
            print(f"   {len(df)} systèmes trouvés dans le CSV")
            
            for index, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO gpr.ref_systemes (id, date_maj, intitule, entite_id, etat, deleted) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        row[0],  # id
                        row[1] if pd.notna(row[1]) else None,  # date_maj
                        row[2],  # intitule
                        row[3] if pd.notna(row[3]) else None,  # entite_id
                        row[4] if pd.notna(row[4]) else None,  # etat
                        row[5] if pd.notna(row[5]) else False  # deleted
                    ))
                except Exception as e:
                    print(f"   ⚠️  Erreur ligne {index + 1}: {e}")
            
            print(f"   ✅ {len(df)} systèmes importés")
        else:
            print(f"   ❌ Fichier {csv_file} non trouvé")
        
        # 3. Importer ref_types
        print("\n🏢 Import de ref_types...")
        csv_file = "sql_data/ref_types.csv"
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file, header=None)
            print(f"   {len(df)} types trouvés dans le CSV")
            
            for index, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO gpr.ref_types (id, date_maj, intitule, system_id, entite_type_id, etat, deleted) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row[0],  # id
                        row[1] if pd.notna(row[1]) else None,  # date_maj
                        row[2],  # intitule
                        row[3] if pd.notna(row[3]) else None,  # system_id
                        row[4] if pd.notna(row[4]) else None,  # entite_type_id
                        row[5] if pd.notna(row[5]) else None,  # etat
                        row[6] if pd.notna(row[6]) else False  # deleted
                    ))
                except Exception as e:
                    print(f"   ⚠️  Erreur ligne {index + 1}: {e}")
            
            print(f"   ✅ {len(df)} types importés")
        else:
            print(f"   ❌ Fichier {csv_file} non trouvé")
        
        # 4. Importer ref_sous_types
        print("\n🏢 Import de ref_sous_types...")
        csv_file = "sql_data/ref_sous_types.csv"
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file, header=None)
            print(f"   {len(df)} sous-types trouvés dans le CSV")
            
            for index, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO gpr.ref_sous_types (id, date_maj, etat, type_id, entitest_id, intitule, deleted) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row[0],  # id
                        row[1] if pd.notna(row[1]) else None,  # date_maj
                        row[2] if pd.notna(row[2]) else None,  # etat
                        row[3] if pd.notna(row[3]) else None,  # type_id
                        row[4] if pd.notna(row[4]) else None,  # entitest_id
                        row[5],  # intitule
                        row[6] if pd.notna(row[6]) else False  # deleted
                    ))
                except Exception as e:
                    print(f"   ⚠️  Erreur ligne {index + 1}: {e}")
            
            print(f"   ✅ {len(df)} sous-types importés")
        else:
            print(f"   ❌ Fichier {csv_file} non trouvé")
        
        # 5. Importer ref_sources
        print("\n🏢 Import de ref_sources...")
        csv_file = "sql_data/ref_sources.csv"
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file, header=None)
            print(f"   {len(df)} sources trouvées dans le CSV")
            
            for index, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO gpr.ref_sources (id, date_maj, etat, intitule, entite_source_id, deleted) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        row[0],  # id
                        row[1] if pd.notna(row[1]) else None,  # date_maj
                        row[2] if pd.notna(row[2]) else None,  # etat
                        row[3],  # intitule
                        row[4] if pd.notna(row[4]) else None,  # entite_source_id
                        row[5] if pd.notna(row[5]) else False  # deleted
                    ))
                except Exception as e:
                    print(f"   ⚠️  Erreur ligne {index + 1}: {e}")
            
            print(f"   ✅ {len(df)} sources importées")
        else:
            print(f"   ❌ Fichier {csv_file} non trouvé")
        
        # 6. Vérifier le résultat
        print("\n✅ Vérification du résultat...")
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_entites")
        entites_count = cursor.fetchone()[0]
        print(f"   Total entités: {entites_count}")
        
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_systemes")
        systemes_count = cursor.fetchone()[0]
        print(f"   Total systèmes: {systemes_count}")
        
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_types")
        types_count = cursor.fetchone()[0]
        print(f"   Total types: {types_count}")
        
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_sous_types")
        sous_types_count = cursor.fetchone()[0]
        print(f"   Total sous-types: {sous_types_count}")
        
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_sources")
        sources_count = cursor.fetchone()[0]
        print(f"   Total sources: {sources_count}")
        
        # Afficher quelques exemples
        print("\n📋 Exemples de données importées:")
        
        cursor.execute("SELECT id, intitule FROM gpr.ref_entites LIMIT 3")
        entites = cursor.fetchall()
        print("   Entités:")
        for entite in entites:
            print(f"      {entite[0]}: {entite[1]}")
        
        cursor.execute("SELECT id, intitule FROM gpr.ref_systemes LIMIT 3")
        systemes = cursor.fetchall()
        print("   Systèmes:")
        for systeme in systemes:
            print(f"      {systeme[0]}: {systeme[1]}")
        
        cursor.execute("SELECT id, intitule FROM gpr.ref_types LIMIT 3")
        types = cursor.fetchall()
        print("   Types:")
        for type_ in types:
            print(f"      {type_[0]}: {type_[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Import des données de référence terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    import_reference_data()
