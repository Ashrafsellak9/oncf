#!/usr/bin/env python3
"""
Check for arcs with null geometry in the database
"""

import psycopg2

def check_null_geometry():
    """Check for arcs with null geometry"""
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        
        cursor = conn.cursor()
        
        print("🔍 Checking for arcs with null geometry...")
        print("=" * 50)
        
        # Check arcs with null geometry
        cursor.execute("""
            SELECT id, nom_axe, geometrie 
            FROM gpr.graphe_arc 
            WHERE geometrie IS NULL 
            LIMIT 10
        """)
        
        null_arcs = cursor.fetchall()
        
        if null_arcs:
            print(f"❌ Found {len(null_arcs)} arcs with null geometry:")
            for arc in null_arcs:
                arc_id, nom_axe, geometrie = arc
                print(f"   Arc {arc_id} ({nom_axe}): {geometrie}")
        else:
            print("✅ No arcs with null geometry found")
        
        # Check arcs with empty string geometry
        cursor.execute("""
            SELECT id, nom_axe, geometrie 
            FROM gpr.graphe_arc 
            WHERE geometrie = '' 
            LIMIT 10
        """)
        
        empty_arcs = cursor.fetchall()
        
        if empty_arcs:
            print(f"\n⚠️ Found {len(empty_arcs)} arcs with empty geometry:")
            for arc in empty_arcs:
                arc_id, nom_axe, geometrie = arc
                print(f"   Arc {arc_id} ({nom_axe}): '{geometrie}'")
        else:
            print("\n✅ No arcs with empty geometry found")
        
        # Check total count vs non-null count
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc WHERE geometrie IS NOT NULL")
        non_null_count = cursor.fetchone()[0]
        
        print(f"\n📊 Summary:")
        print(f"   Total arcs: {total_count}")
        print(f"   Arcs with geometry: {non_null_count}")
        print(f"   Arcs without geometry: {total_count - non_null_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_null_geometry()
