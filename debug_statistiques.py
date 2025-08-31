#!/usr/bin/env python3
"""
Script de débogage pour la page des statistiques
"""

import requests
from bs4 import BeautifulSoup

def debug_statistics_page():
    """Déboguer la page des statistiques"""
    
    print("🔍 Débogage de la page des statistiques")
    print("=" * 50)
    
    # Session pour maintenir l'authentification
    session = requests.Session()
    
    try:
        # 1. Connexion
        print("\n1️⃣ Connexion...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post('http://localhost:5000/login', data=login_data)
        print(f"Status de connexion: {login_response.status_code}")
        
        # 2. Accès à la page des statistiques
        print("\n2️⃣ Accès à la page des statistiques...")
        stats_response = session.get('http://localhost:5000/statistiques')
        print(f"Status de la page: {stats_response.status_code}")
        
        # 3. Analyse du contenu HTML
        print("\n3️⃣ Analyse du contenu HTML...")
        soup = BeautifulSoup(stats_response.text, 'html.parser')
        
        # Vérifier le titre
        title = soup.find('title')
        print(f"Titre de la page: {title.text if title else 'Non trouvé'}")
        
        # Vérifier les scripts
        scripts = soup.find_all('script')
        print(f"Nombre total de scripts: {len(scripts)}")
        
        for i, script in enumerate(scripts):
            src = script.get('src', '')
            if src:
                print(f"  Script {i+1}: {src}")
            else:
                # Script inline
                content = script.string[:100] if script.string else "Vide"
                print(f"  Script {i+1}: Inline - {content}...")
        
        # Vérifier les blocs Jinja2
        print("\n4️⃣ Vérification des blocs Jinja2...")
        
        # Chercher les blocs extra_js
        extra_js_blocks = stats_response.text.count('{% block extra_js %}')
        print(f"Blocs extra_js trouvés: {extra_js_blocks}")
        
        # Chercher les références à statistiques.js
        statistiques_js_count = stats_response.text.count('statistiques.js')
        print(f"Références à statistiques.js: {statistiques_js_count}")
        
        # Chercher les références à chart.js
        chart_js_count = stats_response.text.count('chart.js')
        print(f"Références à chart.js: {chart_js_count}")
        
        # Afficher un extrait du HTML
        print("\n5️⃣ Extrait du HTML (dernières 500 caractères):")
        html_end = stats_response.text[-500:]
        print(html_end)
        
        # Vérifier si le template est correctement étendu
        extends_base = '{% extends "base.html" %}' in stats_response.text
        print(f"\nTemplate étend base.html: {extends_base}")
        
        # Vérifier les éléments principaux
        print("\n6️⃣ Éléments principaux:")
        elements = ['totalGares', 'totalArcs', 'totalAxes', 'totalVilles']
        for element in elements:
            found = element in stats_response.text
            print(f"  {element}: {'✅' if found else '❌'}")
        
        # Vérifier les canvas
        canvas_elements = ['garesTypeChart', 'axesChart', 'timelineChart', 'etatChart']
        for canvas in canvas_elements:
            found = canvas in stats_response.text
            print(f"  {canvas}: {'✅' if found else '❌'}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_statistics_page()
