import os

def cleanup_test_files():
    """Nettoyer les fichiers de test temporaires"""
    
    # Liste des fichiers de test à supprimer
    test_files = [
        'check_gares_csv.py',
        'fix_gares_data.py',
        'test_gares_api.py',
        'test_gares_direct.py',
        'check_gares_structure.py',
        'test_gares_complete.py',
        'test_gares_details.py',
        'test_filtrage_gares.py',
        'cleanup_test_files.py'
    ]
    
    print("🧹 Nettoyage des fichiers de test temporaires...")
    
    for filename in test_files:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"   ✅ Supprimé: {filename}")
            except Exception as e:
                print(f"   ❌ Erreur lors de la suppression de {filename}: {e}")
        else:
            print(f"   ⚠️ Fichier non trouvé: {filename}")
    
    print("\n✅ Nettoyage terminé !")
    print("📁 Les fichiers de test temporaires ont été supprimés")

if __name__ == "__main__":
    cleanup_test_files()
