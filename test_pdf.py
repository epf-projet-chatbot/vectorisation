#!/usr/bin/env python3
"""
Script de test pour valider le fonctionnement de la pipeline avec les PDFs
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent))

from config import config
from loader import process_pdf_files, load_file
from chunker import split_text_into_chunks
from embedder import get_embedding
from search import SemanticSearch
from mongo import get_collection_stats, test_connection


def test_pdf_loading():
    """Test du chargement des PDFs"""
    print("=" * 60)
    print("🧪 TEST 1: CHARGEMENT DES PDFs")
    print("=" * 60)
    
    # Activer le mode test
    config.test_mode = True
    
    # Tester le chargement des PDFs
    pdf_data = process_pdf_files()
    
    print(f"📁 Répertoire de test: {config.get_data_dir()}/root")
    print(f"📄 Nombre de PDFs trouvés: {len(pdf_data)}")
    
    if not pdf_data:
        print("❌ ÉCHEC: Aucun PDF trouvé")
        return False
    
    # Vérifier chaque PDF
    for i, pdf in enumerate(pdf_data, 1):
        filename = os.path.basename(pdf['source'])
        content_length = len(pdf['content'])
        
        print(f"\n📄 PDF {i}: {filename}")
        print(f"   📏 Taille du contenu: {content_length} caractères")
        
        # Afficher un extrait du contenu
        if content_length > 0:
            preview = pdf['content'][:150].replace('\n', ' ')
            print(f"   📝 Aperçu: {preview}...")
            print("   ✅ Contenu extrait avec succès")
        else:
            print("   ❌ Contenu vide")
            return False
    
    print(f"\n✅ TEST 1 RÉUSSI: {len(pdf_data)} PDFs chargés correctement")
    return True


def test_pdf_chunking():
    """Test du découpage en chunks des PDFs"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: DÉCOUPAGE EN CHUNKS")
    print("=" * 60)
    
    # Charger un PDF spécifique pour test
    config.test_mode = True
    pdf_data = process_pdf_files()
    
    if not pdf_data:
        print("❌ ÉCHEC: Aucun PDF disponible pour le test")
        return False
    
    # Prendre le premier PDF avec du contenu
    test_pdf = None
    for pdf in pdf_data:
        if len(pdf['content']) > 100:  # Au moins 100 caractères
            test_pdf = pdf
            break
    
    if not test_pdf:
        print("❌ ÉCHEC: Aucun PDF avec suffisamment de contenu")
        return False
    
    filename = os.path.basename(test_pdf['source'])
    print(f"📄 Test avec: {filename}")
    print(f"📏 Taille originale: {len(test_pdf['content'])} caractères")
    
    # Créer les chunks
    chunks = split_text_into_chunks(test_pdf['content'], chunk_size=500, overlap=100)
    
    print(f"✂️  Chunks créés: {len(chunks)}")
    print(f"📏 Paramètres: chunk_size=500, overlap=100")
    
    # Vérifier quelques chunks
    for i, chunk in enumerate(chunks[:3]):  # Premiers 3 chunks
        print(f"\n📑 Chunk {i+1}:")
        print(f"   📏 Taille: {len(chunk)} caractères")
        print(f"   📝 Aperçu: {chunk[:100]}...")
    
    if len(chunks) > 0:
        print(f"\n✅ TEST 2 RÉUSSI: {len(chunks)} chunks créés")
        return True
    else:
        print("\n❌ TEST 2 ÉCHOUÉ: Aucun chunk créé")
        return False


def test_pdf_embedding():
    """Test de génération d'embeddings pour les PDFs"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: GÉNÉRATION D'EMBEDDINGS")
    print("=" * 60)
    
    # Texte de test extrait d'un PDF
    test_text = "Arrêté du 20 juin 1988 portant fixation de l'assiette forfaitaire des cotisations de sécurité sociale"
    
    print(f"📝 Texte de test: {test_text}")
    
    try:
        # Générer l'embedding
        embedding = get_embedding(test_text)
        
        print(f"🧠 Embedding généré:")
        print(f"   📏 Dimensions: {len(embedding)}")
        print(f"   📊 Type: {type(embedding[0]).__name__}")
        print(f"   📈 Premiers 5 valeurs: {embedding[:5]}")
        
        # Vérifier que l'embedding est valide
        if len(embedding) > 0 and isinstance(embedding[0], float):
            print("\n✅ TEST 3 RÉUSSI: Embedding généré correctement")
            return True
        else:
            print("\n❌ TEST 3 ÉCHOUÉ: Embedding invalide")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 3 ÉCHOUÉ: Erreur lors de la génération - {e}")
        return False


def test_pdf_search():
    """Test de recherche sémantique dans les PDFs"""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: RECHERCHE SÉMANTIQUE")
    print("=" * 60)
    
    try:
        # Vérifier la connexion DB
        test_connection()
        stats = get_collection_stats()
        
        if stats is None:
            print("❌ ÉCHEC: Impossible de se connecter à la base de données")
            return False
        
        # Initialiser le moteur de recherche
        search_engine = SemanticSearch()
        
        # Requêtes de test spécifiques aux PDFs
        test_queries = [
            "cotisations sécurité sociale",
            "analyse des litiges",
            "assiette forfaitaire"
        ]
        
        all_tests_passed = True
        
        for query in test_queries:
            print(f"\n🔍 Test recherche: '{query}'")
            
            try:
                results = search_engine.search(query, top_k=2)
                
                if results:
                    print(f"   ✅ {len(results)} résultat(s) trouvé(s)")
                    
                    # Vérifier si au moins un résultat vient d'un PDF
                    pdf_found = False
                    for result in results:
                        filename = result['document']['filename']
                        if filename.endswith('.pdf'):
                            pdf_found = True
                            similarity = result['similarity']
                            print(f"   📄 PDF trouvé: {os.path.basename(filename)} (similarité: {similarity:.3f})")
                            break
                    
                    if not pdf_found:
                        print("   ⚠️  Aucun résultat PDF trouvé pour cette requête")
                else:
                    print("   ❌ Aucun résultat trouvé")
                    all_tests_passed = False
                    
            except Exception as e:
                print(f"   ❌ Erreur lors de la recherche: {e}")
                all_tests_passed = False
        
        if all_tests_passed:
            print("\n✅ TEST 4 RÉUSSI: Recherche sémantique fonctionnelle")
            return True
        else:
            print("\n❌ TEST 4 PARTIELLEMENT ÉCHOUÉ: Certaines recherches ont échoué")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 4 ÉCHOUÉ: Erreur générale - {e}")
        return False


def run_all_tests():
    """Exécute tous les tests pour les PDFs"""
    print("🚀 DÉBUT DES TESTS PDF")
    print("=" * 60)
    
    tests = [
        ("Chargement des PDFs", test_pdf_loading),
        ("Découpage en chunks", test_pdf_chunking),
        ("Génération d'embeddings", test_pdf_embedding),
        ("Recherche sémantique", test_pdf_search)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ ERREUR CRITIQUE dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\n📊 RÉSULTAT GLOBAL: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS ! Les PDFs fonctionnent correctement.")
        return True
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ. Vérifiez les erreurs ci-dessus.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
