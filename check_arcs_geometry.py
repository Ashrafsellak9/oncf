#!/usr/bin/env python3
"""
Check arcs geometry data in the database
"""

import psycopg2
import json

def check_arcs_geometry():
    """Check the geometry data in the arcs table"""
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            database="oncf_achraf",
            user="postgres",
            password="postgres"
        )
        
        cursor = conn.cursor()
        
        print("🔍 Checking arcs geometry data...")
        print("=" * 50)
        
        # Check total number of arcs
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc")
        total_arcs = cursor.fetchone()[0]
        print(f"📊 Total arcs in database: {total_arcs}")
        
        # Check arcs with valid geometry
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc WHERE geometrie IS NOT NULL")
        arcs_with_geom = cursor.fetchone()[0]
        print(f"✅ Arcs with geometry: {arcs_with_geom}")
        
        # Check arcs with null geometry
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc WHERE geometrie IS NULL")
        arcs_without_geom = cursor.fetchone()[0]
        print(f"❌ Arcs without geometry: {arcs_without_geom}")
        
        # Show sample of arcs with geometry
        print(f"\n🔍 Sample arcs WITH geometry:")
        cursor.execute("""
            SELECT id, nom_axe, geometrie 
            FROM gpr.graphe_arc 
            WHERE geometrie IS NOT NULL 
            LIMIT 5
        """)
        
        arcs_with_geom_data = cursor.fetchall()
        for arc in arcs_with_geom_data:
            arc_id, nom_axe, geom = arc
            print(f"   Arc {arc_id} ({nom_axe}): {geom[:100]}...")
        
        # Show sample of arcs without geometry
        print(f"\n❌ Sample arcs WITHOUT geometry:")
        cursor.execute("""
            SELECT id, nom_axe, geometrie 
            FROM gpr.graphe_arc 
            WHERE geometrie IS NULL 
            LIMIT 5
        """)
        
        arcs_without_geom_data = cursor.fetchall()
        for arc in arcs_without_geom_data:
            arc_id, nom_axe, geom = arc
            print(f"   Arc {arc_id} ({nom_axe}): {geom}")
        
        # Check if there are any arcs with empty string geometry
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc WHERE geometrie = ''")
        arcs_empty_geom = cursor.fetchone()[0]
        print(f"\n⚠️ Arcs with empty string geometry: {arcs_empty_geom}")
        
        # Check the structure of the table
        print(f"\n📋 Table structure:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'gpr' 
            AND table_name = 'graphe_arc'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            col_name, data_type, is_nullable = col
            print(f"   {col_name}: {data_type} ({'NULL' if is_nullable == 'YES' else 'NOT NULL'})")
        
        # Check if there are any arcs with different geometry column names
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'gpr' 
            AND table_name = 'graphe_arc'
            AND column_name LIKE '%geom%'
        """)
        
        geom_columns = cursor.fetchall()
        print(f"\n📍 Geometry-related columns: {[col[0] for col in geom_columns]}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🔧 RECOMMENDATIONS:")
        print(f"1. {arcs_without_geom} arcs need geometry data")
        print(f"2. Check if geometry data was properly imported from CSV")
        print(f"3. Verify the CSV file contains geometry data for all arcs")
        print(f"4. Consider re-importing the arcs data with proper geometry")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_arcs_geometry()
