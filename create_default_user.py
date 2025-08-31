#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur par défaut
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from datetime import datetime

# Configuration de la base de données
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/oncf_achraf"

def create_default_user():
    """Créer un utilisateur administrateur par défaut"""
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT id FROM gpr.users WHERE username = 'admin'")
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("L'utilisateur 'admin' existe déjà.")
            return
        
        # Créer l'utilisateur administrateur
        username = 'admin'
        email = 'admin@oncf.ma'
        password_hash = generate_password_hash('admin123')
        first_name = 'Administrateur'
        last_name = 'ONCF'
        role = 'admin'
        created_at = datetime.utcnow()
        
        # Insérer l'utilisateur
        cursor.execute("""
            INSERT INTO gpr.users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (username, email, password_hash, first_name, last_name, role, True, created_at))
        
        conn.commit()
        print("✅ Utilisateur administrateur créé avec succès!")
        print("📋 Informations de connexion:")
        print("   Nom d'utilisateur: admin")
        print("   Mot de passe: admin123")
        print("   Email: admin@oncf.ma")
        print("   Rôle: Administrateur")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 Création de l'utilisateur administrateur par défaut...")
    create_default_user()
