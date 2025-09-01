#!/usr/bin/env python3
"""
Check the exact format of geometry data in the database
"""

import psycopg2

def check_geometry_format():
    """Check the exact format of geometry data"""
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        
        cursor = conn.cursor()
        
        print("🔍 Checking geometry format...")
        print("=" * 50)
        
        # Check different geometry formats
        cursor.execute("""
            SELECT id, nom_axe, geometrie 
            FROM gpr.graphe_arc 
            WHERE geometrie IS NOT NULL 
            LIMIT 10
        """)
        
        arcs = cursor.fetchall()
        
        for arc in arcs:
            arc_id, nom_axe, geometrie = arc
            print(f"\nArc {arc_id} ({nom_axe}):")
            print(f"   Raw geometry: {geometrie}")
            
            # Check what format it is
            if geometrie.startswith('SRID=3857;LINESTRING('):
                print(f"   ✅ Format: SRID=3857;LINESTRING")
            elif geometrie.startswith('LINESTRING('):
                print(f"   ✅ Format: LINESTRING (no SRID)")
            elif geometrie.startswith('0102000020'):
                print(f"   ✅ Format: WKB hex")
            elif geometrie.startswith('0002000020'):
                print(f"   ✅ Format: WKB hex (big endian)")
            else:
                print(f"   ❓ Format: Unknown - starts with: {geometrie[:20]}...")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_geometry_format()
