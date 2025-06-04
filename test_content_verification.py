#!/usr/bin/env python3
"""
Script de vérification pour s'assurer que le contenu original (non pré-traité) 
est bien stocké dans MongoDB
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mongo import init_connection, client, db, collection
from preprocessor import preprocess_text

def verify_content_storage():
    """Vérifie que le contenu stocké est bien le contenu original (non pré-traité)"""
    # Initialiser la connexion
    init_connection()
    
    # Récupérer quelques documents de test
    sample_docs = list(collection.find().limit(5))
    
    print("=== VÉRIFICATION DU CONTENU STOCKÉ ===")
    print(f"Nombre de documents en base: {collection.count_documents({})}")
    print()
    
    for i, doc in enumerate(sample_docs, 1):
        content = doc.get('content', '')
        processed_content = preprocess_text(content)
        
        print(f"DOCUMENT {i}:")
        print(f"  Source: {doc.get('source', 'Unknown')}")
        print(f"  Taille contenu: {len(content)} caractères")
        print()
        
        # Extraits pour comparaison
        print("  Contenu stocké (premiers 200 chars):")
        print(f"  '{content[:200]}...'")
        print()
        
        print("  Ce même contenu après pré-traitement (premiers 200 chars):")
        print(f"  '{processed_content[:200]}...'")
        print()
        
        # Vérification que le contenu n'est PAS pré-traité
        is_original = content != processed_content
        print(f"  ✓ Contenu original (non pré-traité): {'OUI' if is_original else 'NON'}")
        print()
        
        if not is_original:
            print(f"  ⚠️  PROBLÈME: Le contenu semble être pré-traité!")
        
        print("-" * 70)
        print()

if __name__ == "__main__":
    verify_content_storage()
