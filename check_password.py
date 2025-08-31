#!/usr/bin/env python3
"""
Vérification du mot de passe de l'utilisateur admin
"""

import psycopg2
from werkzeug.security import check_password_hash

def check_admin_password():
    """Vérifier le mot de passe de l'utilisateur admin"""
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        
        cursor = conn.cursor()
        
        # Récupérer l'utilisateur admin
        cursor.execute("SELECT id, username, password_hash FROM gpr.users WHERE username = 'admin'")
        user = cursor.fetchone()
        
        if user:
            user_id, username, password_hash = user
            print(f"✅ Utilisateur trouvé: ID={user_id}, Username={username}")
            print(f"🔐 Hash du mot de passe: {password_hash}")
            
            # Tester différents mots de passe
            test_passwords = ['admin123', 'admin', 'password', '123456']
            
            for password in test_passwords:
                is_valid = check_password_hash(password_hash, password)
                print(f"🔍 Test '{password}': {'✅ Valide' if is_valid else '❌ Invalide'}")
                
        else:
            print("❌ Utilisateur admin non trouvé")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_admin_password()
