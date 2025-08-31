import pandas as pd

# Lire le fichier CSV
df = pd.read_csv("sql_data/axes.csv", header=None)

print(f"📊 Structure du fichier axes.csv: {df.shape[0]} lignes, {df.shape[1]} colonnes")
print("\n📋 Premières 10 lignes:")
for i in range(min(10, len(df))):
    print(f"Ligne {i+1}: {list(df.iloc[i])}")

print(f"\n🔍 Colonnes disponibles:")
for i in range(df.shape[1]):
    print(f"Colonne {i}: {df.iloc[0, i] if len(df) > 0 else 'N/A'}")
