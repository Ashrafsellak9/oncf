#!/usr/bin/env python3
"""
Debug des réponses API
"""

import requests
import json

def debug_response(url, session=None):
    """Debug une réponse API"""
    print(f"🔍 Test de: {url}")
    
    try:
        if session:
            response = session.get(url)
        else:
            response = requests.get(url)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📄 Content Type: {response.headers.get('content-type', 'Non spécifié')}")
        print(f"📏 Content Length: {len(response.content)}")
        
        if response.content:
            print(f"📝 Raw Content: {response.content[:500]}...")
            
            try:
                json_data = response.json()
                print(f"✅ JSON valide: {json.dumps(json_data, indent=2)[:500]}...")
            except json.JSONDecodeError as e:
                print(f"❌ JSON invalide: {e}")
        else:
            print("📭 Contenu vide")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        print("-" * 50)

def main():
    print("🚀 Debug des réponses API")
    print("=" * 50)
    
    # Test sans authentification
    print("🔓 Test sans authentification:")
    debug_response('http://localhost:5000/api/axes?page=1&per_page=10')
    
    # Test avec authentification
    print("🔐 Test avec authentification:")
    session = requests.Session()
    
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        login_response = session.post('http://localhost:5000/login', data=login_data)
        print(f"🔑 Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            debug_response('http://localhost:5000/api/axes?page=1&per_page=10', session)
            debug_response('http://localhost:5000/api/reference/types', session)
        else:
            print("❌ Échec de connexion")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    main()
