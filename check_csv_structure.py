#!/usr/bin/env python3
"""
Script pour vérifier la structure exacte du CSV incidents
"""

import pandas as pd
import os

def check_csv_structure():
    """Vérifier la structure exacte du CSV incidents"""
    
    try:
        print("🔍 Vérification de la structure du CSV incidents")
        print("=" * 60)
        
        csv_file = "sql_data/incidents.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return False
        
        # Lire le CSV sans header
        df = pd.read_csv(csv_file, header=None)
        
        print(f"📊 Structure du CSV:")
        print(f"   Nombre de lignes: {len(df)}")
        print(f"   Nombre de colonnes: {len(df.columns)}")
        
        print(f"\n📋 Colonnes (0-{len(df.columns)-1}):")
        for i in range(len(df.columns)):
            print(f"   {i}: {df.iloc[0, i] if not pd.isna(df.iloc[0, i]) else 'NULL'}")
        
        print(f"\n🔍 Première ligne complète:")
        for i, value in enumerate(df.iloc[0]):
            print(f"   {i}: {value}")
        
        print(f"\n🔍 Deuxième ligne (pour comparaison):")
        for i, value in enumerate(df.iloc[1]):
            print(f"   {i}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    check_csv_structure()
