#!/usr/bin/env python3
"""
Script pour corriger les URLs de base de données dans app.py
"""

import re

def fix_database_url():
    """Corriger les URLs de base de données"""
    try:
        # Lire le fichier
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les occurrences
        old_pattern = r"psycopg2\.connect\(os\.getenv\('DATABASE_URL'\)\)"
        new_replacement = "psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))"
        
        content = re.sub(old_pattern, new_replacement, content)
        
        # Écrire le fichier corrigé
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ URLs de base de données corrigées dans app.py")
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")

if __name__ == "__main__":
    fix_database_url()
