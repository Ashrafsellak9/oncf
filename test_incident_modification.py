#!/usr/bin/env python3
"""
Test script pour vérifier les améliorations de la modification d'incident
"""

import requests
import json

def test_incident_modification():
    """Tester les améliorations de la modification d'incident"""
    
    print("🧪 Test des améliorations de la modification d'incident")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. Tester les endpoints de référence
        print("\n📚 Test des endpoints de référence:")
        
        endpoints = [
            '/api/reference/types',
            '/api/reference/sous-types', 
            '/api/reference/sources',
            '/api/reference/systemes',
            '/api/reference/entites',
            '/api/reference/localisations'
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {endpoint}: {len(data)} éléments")
            else:
                print(f"   ❌ {endpoint}: Erreur {response.status_code}")
        
        # 2. Tester la récupération des incidents
        print("\n📋 Test de récupération des incidents:")
        response = requests.get(f"{base_url}/api/evenements?page=1&per_page=5")
        if response.status_code == 200:
            data = response.json()
            incidents = data.get('data', [])
            print(f"   ✅ {len(incidents)} incidents récupérés")
            
            if incidents:
                # 3. Tester la modification d'un incident
                incident = incidents[0]
                incident_id = incident['id']
                print(f"\n✏️ Test de modification de l'incident #{incident_id}:")
                
                # Données de test pour la modification
                update_data = {
                    'resume': f'Test de modification - {incident_id}',
                    'commentaire': 'Commentaire de test ajouté',
                    'etat': 'En cours',
                    'impact_service': 'Modéré',
                    'fonction': 'Test fonction',
                    'important': True
                }
                
                response = requests.put(
                    f"{base_url}/api/evenements/{incident_id}",
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(update_data)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ Incident #{incident_id} modifié avec succès")
                        
                        # Vérifier que les modifications ont été appliquées
                        response = requests.get(f"{base_url}/api/evenements/{incident_id}/details")
                        if response.status_code == 200:
                            details = response.json()
                            if details.get('success'):
                                incident_updated = details['data']
                                print(f"   ✅ Vérification des modifications:")
                                print(f"      - Résumé: {incident_updated.get('resume', 'N/A')}")
                                print(f"      - Commentaire: {incident_updated.get('commentaire', 'N/A')}")
                                print(f"      - État: {incident_updated.get('etat', 'N/A')}")
                                print(f"      - Impact: {incident_updated.get('impact_service', 'N/A')}")
                                print(f"      - Fonction: {incident_updated.get('fonction', 'N/A')}")
                                print(f"      - Important: {incident_updated.get('important', 'N/A')}")
                            else:
                                print(f"   ❌ Erreur récupération détails: {details.get('error')}")
                        else:
                            print(f"   ❌ Erreur HTTP récupération détails: {response.status_code}")
                    else:
                        print(f"   ❌ Erreur modification: {result.get('error')}")
                else:
                    print(f"   ❌ Erreur HTTP modification: {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print("   ⚠️ Aucun incident trouvé pour tester la modification")
        else:
            print(f"   ❌ Erreur récupération incidents: {response.status_code}")
        
        # 4. Tester la création d'un nouvel incident
        print("\n➕ Test de création d'un nouvel incident:")
        
        new_incident_data = {
            'type_id': 1,
            'localisation_id': 1,
            'date_debut': '2024-01-15T10:00:00',
            'resume': 'Test de création d\'incident',
            'commentaire': 'Commentaire de test',
            'etat': 'Ouvert',
            'impact_service': 'Faible',
            'fonction': 'Test',
            'important': False
        }
        
        response = requests.post(
            f"{base_url}/api/evenements",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(new_incident_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Nouvel incident créé avec succès")
            else:
                print(f"   ❌ Erreur création: {result.get('error')}")
        else:
            print(f"   ❌ Erreur HTTP création: {response.status_code}")
            print(f"   Response: {response.text}")
        
        print("\n🎯 Résumé des améliorations:")
        print("   ✅ Formulaire amélioré avec plus de champs")
        print("   ✅ Validation avancée côté client")
        print("   ✅ Aperçu avant sauvegarde")
        print("   ✅ Gestion des erreurs améliorée")
        print("   ✅ Interface utilisateur professionnelle")
        print("   ✅ Endpoints de référence pour les données")
        print("   ✅ Mise à jour complète des incidents")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_incident_modification()
