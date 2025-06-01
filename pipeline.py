"""
Pipeline complète de traitement des documents :
1. Chargement des documents
2. Découpage en chunks
3. Génération des embeddings
4. Insertion dans MongoDB
"""

import os
import argparse
from typing import Optional

from loader import load_all_documents
from chunker import process_documents_chunks
from embedder import process_chunks_embeddings
from mongo import insert_chunks_batch, clear_collection, get_collection_stats

def run_pipeline(chunk_size: int = 1000, overlap: int = 200, clear_db: bool = False):
    """
    Exécute la pipeline complète de traitement des documents
    
    Args:
        chunk_size: Taille maximale des chunks en caractères
        overlap: Chevauchement entre les chunks
        clear_db: Si True, vide la base de données avant l'insertion
    """
    print("=" * 60)
    print("🚀 DÉMARRAGE DE LA PIPELINE DE VECTORISATION")
    print("=" * 60)
    
    try:
        # Optionnel : vider la base de données
        if clear_db:
            print("\n🗑️  Nettoyage de la base de données...")
            clear_collection()
        
        # Étape 1: Chargement des documents
        print("\n📂 ÉTAPE 1: Chargement des documents")
        print("-" * 40)
        documents = load_all_documents()
        
        if not documents:
            print("❌ Aucun document trouvé. Arrêt de la pipeline.")
            return
        
        print(f"✅ {len(documents)} documents chargés avec succès")
        
        # Étape 2: Découpage en chunks
        print(f"\n✂️  ÉTAPE 2: Découpage en chunks")
        print("-" * 40)
        print(f"Paramètres: chunk_size={chunk_size}, overlap={overlap}")
        chunks = process_documents_chunks(documents, chunk_size, overlap)
        
        if not chunks:
            print("❌ Aucun chunk créé. Arrêt de la pipeline.")
            return
        
        # Étape 3: Génération des embeddings
        print(f"\n🧠 ÉTAPE 3: Génération des embeddings")
        print("-" * 40)
        chunks_with_embeddings = process_chunks_embeddings(chunks)
        
        # Étape 4: Insertion dans MongoDB
        print(f"\n💾 ÉTAPE 4: Insertion dans MongoDB")
        print("-" * 40)
        inserted_ids = insert_chunks_batch(chunks_with_embeddings)
        
        # Statistiques finales
        print(f"\n📊 STATISTIQUES FINALES")
        print("-" * 40)
        print(f"Documents traités: {len(documents)}")
        print(f"Chunks créés: {len(chunks)}")
        print(f"Embeddings générés: {len(chunks_with_embeddings)}")
        print(f"Documents insérés en DB: {len(inserted_ids)}")
        
        get_collection_stats()
        
        print("\n" + "=" * 60)
        print("✅ PIPELINE TERMINÉE AVEC SUCCÈS")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERREUR DANS LA PIPELINE: {str(e)}")
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
    
    args = parser.parse_args()
    
    if args.stats_only:
        print("📊 Statistiques de la base de données:")
        get_collection_stats()
        return
    
    run_pipeline(
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        clear_db=args.clear_db
    )

if __name__ == "__main__":
    main()