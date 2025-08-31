#!/usr/bin/env python3
"""
Vérification de l'utilisateur admin dans la base de données
"""

import psycopg2
import os

def check_user():
    """Vérifier si l'utilisateur admin existe"""
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
        
        # Vérifier si la table users existe
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'gpr' AND table_name = 'users'
        """)
        
        if cursor.fetchone():
            print("✅ Table gpr.users existe")
            
            # Vérifier les utilisateurs
            cursor.execute("SELECT id, username, email FROM gpr.users")
            users = cursor.fetchall()
            
            if users:
                print(f"✅ {len(users)} utilisateur(s) trouvé(s):")
                for user in users:
                    print(f"   - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
            else:
                print("❌ Aucun utilisateur trouvé")
                
        else:
            print("❌ Table gpr.users n'existe pas")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_user()
