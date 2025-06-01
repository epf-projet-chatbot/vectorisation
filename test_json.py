#!/usr/bin/env python3
"""
Script de test pour valider le fonctionnement de la pipeline avec les fichiers JSON
"""

import os
import sys
import json
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent))

from config import config
from loader import process_json_file, load_file
from chunker import split_text_into_chunks
from embedder import get_embedding
from search import SemanticSearch
from mongo import get_collection_stats, test_connection


def test_json_loading():
    """Test du chargement du fichier JSON"""
    print("=" * 60)
    print("🧪 TEST 1: CHARGEMENT DU FICHIER JSON")
    print("=" * 60)
    
    # Activer le mode test
    config.test_mode = True
    
    # Tester le chargement du JSON
    json_data = process_json_file()
    
    print(f"📁 Répertoire de test: {config.get_data_dir()}")
    print(f"📄 Fichier JSON: {config.get_json_filename()}")
    
    if not json_data:
        print("❌ ÉCHEC: Aucun fichier JSON trouvé ou chargé")
        return False
    
    print(f"✅ Fichier JSON chargé avec succès")
    print(f"📏 Type de contenu: {type(json_data['content'])}")
    
    if isinstance(json_data['content'], list):
        print(f"📊 Nombre d'éléments: {len(json_data['content'])}")
        
        # Afficher un aperçu du premier élément
        if len(json_data['content']) > 0:
            first_item = json_data['content'][0]
            print(f"\n📋 Aperçu du premier élément:")
            for key, value in first_item.items():
                if key == 'content' and isinstance(value, list):
                    print(f"   {key}: liste de {len(value)} éléments")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"   {key}: {value[:50]}...")
                else:
                    print(f"   {key}: {value}")
    else:
        print(f"📊 Contenu: {str(json_data['content'])[:200]}...")
    
    print(f"\n✅ TEST 1 RÉUSSI: Fichier JSON chargé et structuré correctement")
    return True


def test_json_content_extraction():
    """Test de l'extraction du contenu des éléments JSON"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: EXTRACTION DU CONTENU JSON")
    print("=" * 60)
    
    # Charger le JSON
    config.test_mode = True
    json_data = process_json_file()
    
    if not json_data:
        print("❌ ÉCHEC: Aucun fichier JSON disponible pour le test")
        return False
    
    # Vérifier la structure du contenu
    content = json_data.get('content', [])
    if not isinstance(content, list) or len(content) == 0:
        print("❌ ÉCHEC: Structure JSON incorrecte ou vide")
        return False
    
    # Tester l'extraction de contenu textuel de différents éléments
    total_text_length = 0
    extracted_fields = []
    
    print(f"📄 Analyse de {len(content)} objets JSON...")
    
    for i, item in enumerate(content[:3]):  # Analyser les 3 premiers
        print(f"\n📋 Objet {i+1}:")
        
        # Extraire les champs textuels principaux
        text_fields = []
        
        if 'title' in item:
            text_fields.append(f"Titre: {item['title']}")
        if 'description' in item:
            text_fields.append(f"Description: {item['description']}")
        if 'budget' in item:
            text_fields.append(f"Budget: {item['budget']}")
        
        # Traiter les objets imbriqués
        if 'client' in item and isinstance(item['client'], dict):
            client = item['client']
            if 'name' in client:
                text_fields.append(f"Client: {client['name']}")
        
        # Traiter les listes (skills, etc.)
        if 'skills' in item and isinstance(item['skills'], list):
            skills = [skill.get('name', '') for skill in item['skills'] if isinstance(skill, dict)]
            if skills:
                text_fields.append(f"Compétences: {', '.join(skills)}")
        
        # Combiner tout le texte
        combined_text = " | ".join(text_fields)
        text_length = len(combined_text)
        total_text_length += text_length
        
        print(f"   📏 Texte extrait: {text_length} caractères")
        print(f"   📝 Aperçu: {combined_text[:100]}...")
        
        extracted_fields.extend(text_fields)
    
    print(f"\n📊 Résumé de l'extraction:")
    print(f"   📏 Longueur totale du texte: {total_text_length} caractères")
    print(f"   📄 Champs extraits: {len(extracted_fields)}")
    
    if total_text_length > 0:
        print(f"\n✅ TEST 2 RÉUSSI: Contenu JSON extrait avec succès")
        return True
    else:
        print(f"\n❌ TEST 2 ÉCHOUÉ: Aucun contenu textuel extrait")
        return False


def test_json_chunking():
    """Test du découpage en chunks du contenu JSON"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: DÉCOUPAGE EN CHUNKS DU JSON")
    print("=" * 60)
    
    # Charger le JSON et extraire le contenu
    config.test_mode = True
    json_data = process_json_file()
    
    if not json_data:
        print("❌ ÉCHEC: Aucun fichier JSON disponible pour le test")
        return False
    
    # Simuler l'extraction du contenu comme dans le loader
    full_content = json.dumps(json_data['content'], ensure_ascii=False, indent=2)
    
    print(f"📄 Contenu JSON:")
    print(f"   📏 Taille originale: {len(full_content)} caractères")
    
    # Créer les chunks
    chunks = split_text_into_chunks(full_content, chunk_size=800, overlap=100)
    
    print(f"✂️  Résultat du chunking:")
    print(f"   📑 Chunks créés: {len(chunks)}")
    print(f"   📏 Paramètres: chunk_size=800, overlap=100")
    
    # Vérifier quelques chunks
    for i, chunk in enumerate(chunks[:2]):  # Premiers 2 chunks
        print(f"\n📑 Chunk {i+1}:")
        print(f"   📏 Taille: {len(chunk)} caractères")
        print(f"   📝 Aperçu: {chunk[:120]}...")
    
    if len(chunks) > 0:
        print(f"\n✅ TEST 3 RÉUSSI: {len(chunks)} chunks créés à partir du JSON")
        return True
    else:
        print(f"\n❌ TEST 3 ÉCHOUÉ: Aucun chunk créé")
        return False


def test_json_embedding():
    """Test de génération d'embeddings pour le contenu JSON"""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: GÉNÉRATION D'EMBEDDINGS POUR JSON")
    print("=" * 60)
    
    # Texte de test extrait du JSON
    test_text = "Développement application mobile de conseil juridique. Budget: De 5 000€ à 15 000€. Client: Cabinet d'Avocats Durand"
    
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
            print("\n✅ TEST 4 RÉUSSI: Embedding généré correctement pour le contenu JSON")
            return True
        else:
            print("\n❌ TEST 4 ÉCHOUÉ: Embedding invalide")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 4 ÉCHOUÉ: Erreur lors de la génération - {e}")
        return False


def test_json_search():
    """Test de recherche sémantique dans le contenu JSON"""
    print("\n" + "=" * 60)
    print("🧪 TEST 5: RECHERCHE SÉMANTIQUE DANS LE JSON")
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
        
        # Requêtes de test spécifiques au contenu JSON
        test_queries = [
            "développement application mobile",
            "conseil juridique",
            "RGPD conformité",
            "contrat commercial",
            "cabinet avocat"
        ]
        
        all_tests_passed = True
        
        for query in test_queries:
            print(f"\n🔍 Test recherche: '{query}'")
            
            try:
                results = search_engine.search(query, top_k=2)
                
                if results:
                    print(f"   ✅ {len(results)} résultat(s) trouvé(s)")
                    
                    # Vérifier si au moins un résultat vient du JSON
                    json_found = False
                    for result in results:
                        filename = result['document']['filename']
                        if filename.endswith('.json'):
                            json_found = True
                            similarity = result['similarity']
                            print(f"   📄 JSON trouvé: {os.path.basename(filename)} (similarité: {similarity:.3f})")
                            break
                    
                    if not json_found:
                        print("   ⚠️  Aucun résultat JSON trouvé pour cette requête")
                else:
                    print("   ❌ Aucun résultat trouvé")
                    all_tests_passed = False
                    
            except Exception as e:
                print(f"   ❌ Erreur lors de la recherche: {e}")
                all_tests_passed = False
        
        if all_tests_passed:
            print("\n✅ TEST 5 RÉUSSI: Recherche sémantique fonctionnelle pour le JSON")
            return True
        else:
            print("\n❌ TEST 5 PARTIELLEMENT ÉCHOUÉ: Certaines recherches ont échoué")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 5 ÉCHOUÉ: Erreur générale - {e}")
        return False


def run_all_tests():
    """Exécute tous les tests pour les fichiers JSON"""
    print("🚀 DÉBUT DES TESTS JSON")
    print("=" * 60)
    
    tests = [
        ("Chargement du fichier JSON", test_json_loading),
        ("Extraction du contenu JSON", test_json_content_extraction),
        ("Découpage en chunks du JSON", test_json_chunking),
        ("Génération d'embeddings pour JSON", test_json_embedding),
        ("Recherche sémantique dans le JSON", test_json_search)
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
    print("📋 RÉSUMÉ DES TESTS JSON")
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
        print("🎉 TOUS LES TESTS JSON SONT PASSÉS ! Les fichiers JSON fonctionnent correctement.")
        return True
    else:
        print("⚠️  CERTAINS TESTS JSON ONT ÉCHOUÉ. Vérifiez les erreurs ci-dessus.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
