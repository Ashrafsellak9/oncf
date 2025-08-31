#!/usr/bin/env python3
"""
Script de test final pour vérifier que toutes les corrections fonctionnent
"""

import requests
import json
import time

def test_application():
    """Tester l'application complète"""
    base_url = "http://localhost:5000"
    
    print("🧪 Test final de l'application ONCF EMS")
    print("=" * 50)
    
    # Test 1: Vérifier que l'application répond
    print("1. Test de connectivité...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 302:  # Redirection vers login
            print("✅ Application accessible (redirection vers login)")
        else:
            print(f"⚠️ Application accessible (code: {response.status_code})")
    except Exception as e:
        print(f"❌ Impossible d'accéder à l'application: {e}")
        return False
    
    # Test 2: Test de connexion
    print("\n2. Test de connexion...")
    session = requests.Session()
    
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'remember_me': False
    }
    
    try:
        login_response = session.post(f"{base_url}/login", data=login_data, timeout=10)
        if login_response.status_code == 200:
            print("✅ Connexion réussie")
        else:
            print(f"❌ Échec de la connexion (code: {login_response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test 3: Test des endpoints protégés
    print("\n3. Test des endpoints protégés...")
    
    protected_endpoints = [
        ("/api/axes", "Axes"),
        ("/api/reference/types", "Types de référence"),
        ("/api/reference/sous-types", "Sous-types"),
        ("/api/reference/systemes", "Systèmes"),
        ("/api/reference/sources", "Sources"),
        ("/api/reference/entites", "Entités"),
        ("/api/statistics", "Statistiques")
    ]
    
    success_count = 0
    for endpoint, name in protected_endpoints:
        try:
            response = session.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ {name}: OK")
                        success_count += 1
                    else:
                        print(f"⚠️ {name}: Erreur API - {data.get('error', 'Erreur inconnue')}")
                except json.JSONDecodeError:
                    print(f"⚠️ {name}: Réponse non-JSON")
            else:
                print(f"❌ {name}: Code HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Erreur - {e}")
    
    print(f"\n📊 Résultat: {success_count}/{len(protected_endpoints)} endpoints fonctionnels")
    
    # Test 4: Test des pages principales
    print("\n4. Test des pages principales...")
    
    pages = [
        ("/dashboard", "Dashboard"),
        ("/carte", "Carte"),
        ("/axes", "Axes"),
        ("/reference", "Référence"),
        ("/gares", "Gares"),
        ("/incidents", "Incidents")
    ]
    
    page_success = 0
    for page, name in pages:
        try:
            response = session.get(f"{base_url}{page}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Accessible")
                page_success += 1
            else:
                print(f"❌ {name}: Code HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Erreur - {e}")
    
    print(f"\n📊 Résultat: {page_success}/{len(pages)} pages accessibles")
    
    # Test 5: Test des endpoints publics
    print("\n5. Test des endpoints publics...")
    
    public_endpoints = [
        ("/api/gares", "Gares"),
        ("/api/gares/filters", "Filtres gares"),
        ("/api/evenements", "Événements"),
        ("/api/types-incidents", "Types incidents"),
        ("/api/localisations", "Localisations"),
        ("/api/statistiques", "Statistiques")
    ]
    
    public_success = 0
    for endpoint, name in public_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ {name}: OK")
                        public_success += 1
                    else:
                        print(f"⚠️ {name}: Erreur API - {data.get('error', 'Erreur inconnue')}")
                except json.JSONDecodeError:
                    print(f"⚠️ {name}: Réponse non-JSON")
            else:
                print(f"❌ {name}: Code HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Erreur - {e}")
    
    print(f"\n📊 Résultat: {public_success}/{len(public_endpoints)} endpoints publics fonctionnels")
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 50)
    print(f"🔐 Authentification: {'✅ OK' if login_response.status_code == 200 else '❌ ÉCHEC'}")
    print(f"🛡️ Endpoints protégés: {success_count}/{len(protected_endpoints)} fonctionnels")
    print(f"🌐 Pages principales: {page_success}/{len(pages)} accessibles")
    print(f"📡 Endpoints publics: {public_success}/{len(public_endpoints)} fonctionnels")
    
    total_tests = 1 + len(protected_endpoints) + len(pages) + len(public_endpoints)
    total_success = (1 if login_response.status_code == 200 else 0) + success_count + page_success + public_success
    
    print(f"\n🎯 Score global: {total_success}/{total_tests} ({total_success/total_tests*100:.1f}%)")
    
    if total_success/total_tests >= 0.8:
        print("🎉 Application fonctionnelle !")
        return True
    else:
        print("⚠️ Quelques problèmes détectés")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage du test final...")
    print("Assurez-vous que l'application est en cours d'exécution sur http://localhost:5000")
    print()
    
    success = test_application()
    
    if success:
        print("\n✅ Tests terminés avec succès !")
        print("L'application est prête à être utilisée.")
    else:
        print("\n❌ Certains tests ont échoué.")
        print("Vérifiez les logs de l'application pour plus de détails.")
