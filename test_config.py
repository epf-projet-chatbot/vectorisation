#!/usr/bin/env python3
"""
Script de test de la configuration et des connexions
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_config():
    """Teste la configuration"""
    print("🔧 Test de la configuration")
    print("-" * 40)
    
    try:
        from config import config
        
        print(f"✅ Database: {config.database_name}")
        print(f"✅ Collection: {config.collection_name}")
        print(f"✅ Mongo URL: {config.mongo_url}")
        print(f"✅ Chunk size: {config.chunk_size}")
        print(f"✅ Test mode: {config.test_mode}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False

def test_mongo_connection():
    """Teste la connexion MongoDB"""
    print("\n🔗 Test de connexion MongoDB")
    print("-" * 40)
    
    try:
        from mongo import init_connection, test_connection, count_documents
        
        # Initialiser la connexion
        if init_connection():
            print("✅ Connexion initialisée")
            
            # Tester la connexion
            if test_connection():
                print("✅ Test de ping réussi")
                
                # Compter les documents
                doc_count = count_documents()
                print(f"✅ Documents dans la collection: {doc_count}")
                
                return True
            else:
                print("❌ Test de ping échoué")
                return False
        else:
            print("❌ Échec d'initialisation")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("💡 Vérifiez vos paramètres MongoDB dans le fichier .env")
        return False

def test_rag_functions():
    """Teste les fonctions RAG"""
    print("\n🤖 Test des fonctions RAG")
    print("-" * 40)
    
    try:
        from rag import make_vector, k_context_vectors
        
        # Test de vectorisation
        test_text = "Bonjour, ceci est un test"
        vector = make_vector(test_text)
        print(f"✅ Vectorisation réussie (dimension: {len(vector)})")
        
        # Test de recherche de contexte
        context = k_context_vectors(vector, k=3)
        print(f"✅ Recherche de contexte réussie ({len(context)} résultats)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur RAG: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 TEST DE CONFIGURATION ET CONNEXIONS")
    print("=" * 50)
    
    success = True
    
    # Test de configuration
    success &= test_config()
    
    # Test de connexion MongoDB
    success &= test_mongo_connection()
    
    # Test des fonctions RAG
    success &= test_rag_functions()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Tous les tests sont passés avec succès!")
        print("🎉 Votre système RAG est prêt à être utilisé")
    else:
        print("❌ Certains tests ont échoué")
        print("💡 Vérifiez votre configuration dans le fichier .env")
    
    return success

if __name__ == "__main__":
    main()
