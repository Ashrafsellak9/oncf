#!/usr/bin/env python3
"""
Test spécifique pour vérifier l'affichage des données sur les pages axes et statistiques
"""

import requests
import json
from datetime import datetime

def test_axes_data():
    """Test des données des axes"""
    print("🧪 Test des données des axes...")
    
    try:
        # Test de l'endpoint API des axes
        response = requests.get('http://localhost:5000/api/axes?page=1&per_page=10')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                axes_count = len(data.get('data', []))
                total = data.get('pagination', {}).get('total', 0)
                print(f"✅ API Axes: {axes_count} axes affichés sur {total} au total")
                return True
            else:
                print(f"❌ API Axes: Erreur - {data.get('error', 'Erreur inconnue')}")
                return False
        else:
            print(f"❌ API Axes: Code d'erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Axes: Exception - {e}")
        return False

def test_statistics_data():
    """Test des données des statistiques"""
    print("🧪 Test des données des statistiques...")
    
    try:
        # Test de l'endpoint API des statistiques
        response = requests.get('http://localhost:5000/api/statistiques')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('data', {})
                
                # Vérifier les différentes sections
                sections = ['gares', 'axes', 'evenements', 'types']
                for section in sections:
                    if section in stats:
                        print(f"✅ Statistiques {section}: Données disponibles")
                    else:
                        print(f"⚠️ Statistiques {section}: Pas de données")
                
                return True
            else:
                print(f"❌ API Statistiques: Erreur - {data.get('error', 'Erreur inconnue')}")
                return False
        else:
            print(f"❌ API Statistiques: Code d'erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Statistiques: Exception - {e}")
        return False

def test_reference_data():
    """Test des données de référence"""
    print("🧪 Test des données de référence...")
    
    endpoints = [
        ('types', 'Types'),
        ('sous-types', 'Sous-types'),
        ('systemes', 'Systèmes'),
        ('sources', 'Sources'),
        ('entites', 'Entités')
    ]
    
    success_count = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'http://localhost:5000/api/{endpoint}')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    count = len(data.get('data', []))
                    print(f"✅ {name}: {count} éléments")
                    success_count += 1
                else:
                    print(f"❌ {name}: Erreur - {data.get('error', 'Erreur inconnue')}")
            else:
                print(f"❌ {name}: Code d'erreur {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")
    
    return success_count == len(endpoints)

def main():
    print("🚀 Test spécifique des données des pages")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Tests
    axes_ok = test_axes_data()
    print()
    
    stats_ok = test_statistics_data()
    print()
    
    ref_ok = test_reference_data()
    print()
    
    # Résumé
    print("=" * 50)
    print("📊 RÉSUMÉ")
    print("=" * 50)
    print(f"📈 Données des axes: {'✅ OK' if axes_ok else '❌ ÉCHEC'}")
    print(f"📊 Données des statistiques: {'✅ OK' if stats_ok else '❌ ÉCHEC'}")
    print(f"📋 Données de référence: {'✅ OK' if ref_ok else '❌ ÉCHEC'}")
    
    if axes_ok and stats_ok and ref_ok:
        print("\n🎉 Toutes les données sont correctement affichées !")
    else:
        print("\n⚠️ Certaines données ne s'affichent pas correctement.")
        print("Vérifiez les logs de l'application pour plus de détails.")

if __name__ == "__main__":
    main()
