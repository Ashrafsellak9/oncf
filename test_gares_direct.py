import psycopg2
import psycopg2.extras

def test_gares_direct():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Vérifier les données des gares
        cursor.execute("""
            SELECT id, nom, code, ville, axe, type, etat, pk_debut
            FROM gpr.gpd_gares_ref 
            ORDER BY id
            LIMIT 10
        """)
        
        gares = cursor.fetchall()
        print(f"📊 Total gares dans la base: {len(gares)}")
        
        print("\n📋 Gares avec leurs détails:")
        for gare in gares:
            print(f"   - ID: {gare['id']}, Nom: {gare['nom']}, Code: {gare['code']}, Ville: {gare['ville']}, Axe: {gare['axe']}, Type: {gare['type']}, État: {gare['etat']}")
        
        # Vérifier le total
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total gares dans la table: {total}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_gares_direct()
