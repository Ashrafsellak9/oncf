import pandas as pd

def check_gares_csv():
    try:
        # Lire le fichier CSV
        df = pd.read_csv("sql_data/gares.csv", header=None)
        
        print(f"📊 Structure du fichier gares.csv: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        print(f"📋 Colonnes disponibles: {list(df.columns)}")
        
        print("\n📋 Premières 5 lignes:")
        for i in range(min(5, len(df))):
            print(f"Ligne {i+1}: {list(df.iloc[i])}")
        
        print(f"\n🔍 Analyse des colonnes:")
        for i in range(df.shape[1]):
            col_data = df.iloc[:, i]
            unique_values = col_data.dropna().unique()
            print(f"Colonne {i}: {len(unique_values)} valeurs uniques")
            print(f"   Exemples: {unique_values[:5]}")
            print()
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_gares_csv()
