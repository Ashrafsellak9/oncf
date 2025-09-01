#!/usr/bin/env python3
"""
Script pour vérifier la structure de la table gpd_gares_ref
"""

import psycopg2

try:
    conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/oncf_achraf')
    cur = conn.cursor()
    
    # Check ge_evenement table structure
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'ge_evenement' AND table_schema = 'gpr' ORDER BY ordinal_position")
    columns = [row[0] for row in cur.fetchall()]
    print("ge_evenement columns:", columns)
    
    # Check a few sample rows
    cur.execute("SELECT * FROM gpr.ge_evenement LIMIT 3")
    rows = cur.fetchall()
    print("\nSample rows:")
    for row in rows:
        print(row)
    
    conn.close()
    
except Exception as e:
    print("Error:", e)
