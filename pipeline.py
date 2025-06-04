"""
Pipeline complète de traitement des documents pour le chatbot juridique

MODES D'UTILISATION :

1. MODE TEST (--test) :
   - Utilise un petit dataset de 7 fichiers (3 MD, 3 PDF, 1 JSON)
   - Données dans ./data_test/
   - Idéal pour développement et validation rapide
   - Commande : python pipeline.py --test

2. MODE PRODUCTION (par défaut) :
   - Traite tous les documents du projet
   - Données dans ./data/
   - Pour déploiement en production
   - Commande : python pipeline.py

ÉTAPES DU PIPELINE :
1. Chargement des documents (Markdown, PDF, JSON)
2. Découpage en chunks avec chevauchement
3. Génération des embeddings (multilingual-e5-small)
4. Insertion en MongoDB par lots
"""

import os
import argparse
from typing import Optional

from loader import load_all_documents
from chunker import process_documents_chunks
from embedder import process_chunks_embeddings
from mongo import insert_chunks_batch, clear_collection, get_collection_stats
from config import config
from preprocessor import preprocess_text

def run_pipeline(chunk_size: int = 1000, overlap: int = 200, clear_db: bool = False, test_mode: bool = False):
    """
    Exécute la pipeline complète de traitement des documents
    
    Args:
        chunk_size: Taille maximale des chunks en caractères
        overlap: Chevauchement entre les chunks
        clear_db: Si True, vide la base de données avant l'insertion
        test_mode: Si True, utilise les données de test (./data_test/)
    """
    # Mise à jour de la configuration globale
    config.test_mode = test_mode
    config.chunk_size = chunk_size
    config.chunk_overlap = overlap
    
    mode_text = "MODE TEST" if test_mode else "MODE PRODUCTION"
    print("=" * 60)
    print(f"{mode_text} - PIPELINE DE VECTORISATION")
    print("=" * 60)
    
    try:
        # Optionnel : vider la base de données
        if clear_db:
            print("\nNettoyage de la base de données...")
            clear_collection()
        
        # Étape 1: Chargement des documents
        print("\nETAPE 1: Chargement des documents")
        print("-" * 40)
        documents = load_all_documents()
        
        if not documents:
            print("Aucun document trouvé. Arrêt de la pipeline.")
            return
        
        print(f"{len(documents)} documents chargés avec succès")
        
        # Étape 2: Découpage en chunks
        print(f"\nETAPE 2: Découpage en chunks")
        print("-" * 40)
        print(f"Paramètres: chunk_size={chunk_size}, overlap={overlap}")
        chunks = process_documents_chunks(documents, chunk_size, overlap)
        
        if not chunks:
            print("Aucun chunk créé. Arrêt de la pipeline.")
            return
        
        print(f"{len(chunks)} chunks créés avec succès")
        
        # Étape 2.2: Pré-traitement des chunks
        print(f"\nETAPE 2.2: Pré-traitement des chunks")
        print("-" * 40)
        for chunk in chunks:
            # Stocker le contenu original
            chunk['original_content'] = chunk['content']
            # Créer le contenu prétraité pour les embeddings
            chunk['preprocessed_content'] = preprocess_text(chunk['content'])
        print("Pré-traitement des chunks terminé")
        
        # Étape 3: Génération des embeddings
        print(f"\nETAPE 3: Génération des embeddings")
        print("-" * 40)
        chunks_with_embeddings = process_chunks_embeddings(chunks)
        
        # Étape 4: Insertion dans MongoDB
        print(f"\nETAPE 4: Insertion dans MongoDB")
        print("-" * 40)
        insert_chunks_batch(chunks_with_embeddings, batch_size=config.batch_size)
        
        # Statistiques finales
        print(f"\nSTATISTIQUES FINALES")
        print("-" * 40)
        print(f"Documents traités: {len(documents)}")
        print(f"Chunks créés: {len(chunks)}")
        print(f"Embeddings générés: {len(chunks_with_embeddings)}")
        
        stats = get_collection_stats()
        print(f"Documents en base: {stats['total_documents']}")
        
        print("\n" + "=" * 60)
        print("PIPELINE TERMINÉE AVEC SUCCÈS")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERREUR DANS LA PIPELINE: {str(e)}")
        raise

def main():
    """Point d'entrée principal avec arguments en ligne de commande"""
    parser = argparse.ArgumentParser(description="Pipeline de vectorisation de documents")
    parser.add_argument("--chunk-size", type=int, default=1000, 
                       help="Taille maximale des chunks en caractères (défaut: 1000)")
    parser.add_argument("--overlap", type=int, default=200,
                       help="Chevauchement entre chunks en caractères (défaut: 200)")
    parser.add_argument("--clear-db", action="store_true",
                       help="Vider la base de données avant l'insertion")
    parser.add_argument("--stats-only", action="store_true",
                       help="Afficher uniquement les statistiques de la DB")
    parser.add_argument("--test", action="store_true",
                       help="Utiliser les données de test (mode test)")
    
    args = parser.parse_args()
    
    if args.stats_only:
        print("Statistiques de la base de données:")
        stats = get_collection_stats()
        print(f"Total documents: {stats['total_documents']}")
        print(f"Fichiers uniques: {stats['unique_files']}")
        for ext, count in stats.get('file_types', {}).items():
            print(f"  .{ext}: {count} fichier(s)")
        return
    
    run_pipeline(
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        clear_db=args.clear_db,
        test_mode=args.test
    )

if __name__ == "__main__":
    main()
