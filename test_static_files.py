#!/usr/bin/env python3
"""
Test de l'accessibilité des fichiers statiques
"""

import requests

def test_static_files():
    """Test de l'accessibilité des fichiers statiques"""
    print("🧪 Test des fichiers statiques...")
    
    static_files = [
        '/static/js/axes.js',
        '/static/js/main.js',
        '/static/js/gares.js',
        '/static/js/incidents.js',
        '/static/js/reference.js',
        '/static/css/style.css'
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f'http://localhost:5000{file_path}')
            if response.status_code == 200:
                print(f"✅ {file_path} - Accessible ({len(response.content)} bytes)")
            else:
                print(f"❌ {file_path} - Erreur {response.status_code}")
        except Exception as e:
            print(f"❌ {file_path} - Exception: {e}")

def main():
    print("🚀 Test de l'accessibilité des fichiers statiques")
    print("=" * 60)
    
    test_static_files()

if __name__ == "__main__":
    main()
