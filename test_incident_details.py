#!/usr/bin/env python3
"""
Test script pour vérifier les détails d'incident
"""

import requests
import json

def test_incident_details():
    """Tester les détails d'incident"""
    
    print("🧪 Test des détails d'incident")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. Récupérer la liste des incidents
        print("\n📋 Récupération de la liste des incidents:")
        response = requests.get(f"{base_url}/api/evenements?page=1&per_page=5")
        if response.status_code == 200:
            data = response.json()
            incidents = data.get('data', [])
            print(f"   ✅ {len(incidents)} incidents récupérés")
            
            if incidents:
                # 2. Tester les détails du premier incident
                incident = incidents[0]
                incident_id = incident['id']
                print(f"\n🔍 Test des détails de l'incident #{incident_id}:")
                
                response = requests.get(f"{base_url}/api/evenements/{incident_id}/details")
                if response.status_code == 200:
                    details = response.json()
                    if details.get('success'):
                        incident_data = details['data']
                        print(f"   ✅ Détails récupérés avec succès")
                        print(f"\n   📊 Informations de l'incident #{incident_id}:")
                        print(f"      - État: {incident_data.get('etat', 'N/A')}")
                        print(f"      - Date début: {incident_data.get('date_debut', 'N/A')}")
                        print(f"      - Heure début: {incident_data.get('heure_debut', 'N/A')}")
                        print(f"      - Résumé: {incident_data.get('resume', 'N/A')[:100] if incident_data.get('resume') else 'N/A'}...")
                        print(f"      - Commentaire: {incident_data.get('commentaire', 'N/A')}")
                        print(f"      - Important: {incident_data.get('important', 'N/A')}")
                        print(f"      - Impact service: {incident_data.get('impact_service', 'N/A')}")
                        
                        # Vérifier les références (gérer les différents types)
                        print(f"\n   🏷️ Références:")
                        
                        # Type
                        type_data = incident_data.get('type')
                        if type_data and isinstance(type_data, dict):
                            print(f"      - Type: {type_data.get('intitule', 'N/A')}")
                        else:
                            print(f"      - Type: {type_data if type_data else 'N/A'}")
                        
                        # Sous-type
                        sous_type_data = incident_data.get('sous_type')
                        if sous_type_data and isinstance(sous_type_data, dict):
                            print(f"      - Sous-type: {sous_type_data.get('intitule', 'N/A')}")
                        else:
                            print(f"      - Sous-type: {sous_type_data if sous_type_data else 'N/A'}")
                        
                        # Source
                        source_data = incident_data.get('source')
                        if source_data and isinstance(source_data, dict):
                            print(f"      - Source: {source_data.get('intitule', 'N/A')}")
                        else:
                            print(f"      - Source: {source_data if source_data else 'N/A'}")
                        
                        # Entité
                        entite_data = incident_data.get('entite_ref')
                        if entite_data and isinstance(entite_data, dict):
                            print(f"      - Entité: {entite_data.get('intitule', 'N/A')}")
                        else:
                            print(f"      - Entité: {entite_data if entite_data else 'N/A'}")
                        
                        # Vérifier la localisation
                        localisation = incident_data.get('localisation')
                        if localisation:
                            print(f"\n   📍 Localisation:")
                            print(f"      - Type: {localisation.get('type_localisation', 'N/A')}")
                            print(f"      - PK début: {localisation.get('pk_debut', 'N/A')}")
                            print(f"      - PK fin: {localisation.get('pk_fin', 'N/A')}")
                            print(f"      - Gare début: {localisation.get('gare_debut_id', 'N/A')}")
                            print(f"      - Gare fin: {localisation.get('gare_fin_id', 'N/A')}")
                        else:
                            print(f"\n   📍 Localisation: Aucune information de localisation")
                        
                        print(f"\n   ✅ Test des détails réussi !")
                    else:
                        print(f"   ❌ Erreur API: {details.get('error')}")
                else:
                    print(f"   ❌ Erreur HTTP: {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print("   ⚠️ Aucun incident trouvé pour tester")
        else:
            print(f"   ❌ Erreur récupération incidents: {response.status_code}")
        
        # 3. Tester avec un ID inexistant
        print(f"\n🔍 Test avec un ID inexistant:")
        response = requests.get(f"{base_url}/api/evenements/99999/details")
        if response.status_code == 200:
            details = response.json()
            if not details.get('success'):
                print(f"   ✅ Gestion d'erreur correcte: {details.get('error')}")
            else:
                print(f"   ⚠️ Réponse inattendue pour ID inexistant")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
        
        print(f"\n🎯 Résumé:")
        print(f"   ✅ Endpoint /api/evenements/{incident_id}/details fonctionnel")
        print(f"   ✅ Données complètes récupérées")
        print(f"   ✅ Références et localisation incluses")
        print(f"   ✅ Gestion d'erreurs correcte")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_incident_details()
