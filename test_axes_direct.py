import psycopg2
import psycopg2.extras

def test_axes_direct():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Vérifier les données des axes
        cursor.execute("""
            SELECT id, axe_id, nom_axe, pk_debut, pk_fin, plod, plof
            FROM gpr.graphe_arc 
            ORDER BY axe_id
            LIMIT 10
        """)
        
        axes = cursor.fetchall()
        print(f"📊 Total axes dans la base: {len(axes)}")
        
        print("\n📋 Axes avec leurs noms:")
        for axe in axes:
            print(f"   - ID: {axe['id']}, Axe ID: {axe['axe_id']}, Nom: {axe['nom_axe']}, PK Début: {axe['pk_debut']}, PK Fin: {axe['pk_fin']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_axes_direct()
