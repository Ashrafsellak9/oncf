import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_incidents():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor()
        
        # Vérifier le nombre d'incidents
        cursor.execute('SELECT COUNT(*) FROM ge_evenement')
        count = cursor.fetchone()[0]
        print(f'Nombre d\'incidents dans ge_evenement: {count}')
        
        # Vérifier le schéma
        cursor.execute("SELECT current_schema()")
        schema = cursor.fetchone()[0]
        print(f'Schéma actuel: {schema}')
        
        # Vérifier si la table existe dans le schéma gpr
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'gpr' AND table_name = 'ge_evenement')")
        exists_in_gpr = cursor.fetchone()[0]
        print(f'Table ge_evenement existe dans schéma gpr: {exists_in_gpr}')
        
        # Récupérer quelques incidents
        if count > 0:
            cursor.execute('SELECT id, date_debut, etat, resume FROM ge_evenement LIMIT 3')
            incidents = cursor.fetchall()
            print('\nPremiers incidents:')
            for incident in incidents:
                print(f'ID: {incident[0]}, Date: {incident[1]}, État: {incident[2]}, Résumé: {incident[3][:50] if incident[3] else "Aucun"}...')
        
        conn.close()
        
    except Exception as e:
        print(f'Erreur: {e}')

if __name__ == '__main__':
    check_incidents()
