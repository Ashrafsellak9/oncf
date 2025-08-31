#!/usr/bin/env python3
"""
Script pour vérifier la vraie structure de la table ge_evenement
"""

import psycopg2
import os

def check_real_structure():
    """Vérifier la vraie structure de la table ge_evenement"""
    
    try:
        print("🔍 Vérification de la vraie structure de ge_evenement")
        print("=" * 60)
        
        # Se connecter à la base de données
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        # 1. Vérifier la structure de la table ge_evenement
        print("\n📋 Structure de la table ge_evenement:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'ge_evenement' 
            AND table_schema = 'gpr' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # 2. Vérifier la structure de la table ge_localisation
        print("\n📋 Structure de la table ge_localisation:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'ge_localisation' 
            AND table_schema = 'gpr' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # 3. Vérifier quelques exemples de données actuelles
        print("\n📊 Exemples de données actuelles dans ge_evenement:")
        cursor.execute("""
            SELECT * FROM gpr.ge_evenement LIMIT 1
        """)
        
        incident = cursor.fetchone()
        if incident:
            print(f"   Incident trouvé avec {len(incident)} colonnes")
            print(f"   Première ligne: {incident}")
        else:
            print("   Aucun incident trouvé")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_real_structure()
