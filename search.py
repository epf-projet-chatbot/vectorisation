"""
Module de recherche sémantique dans la base de données vectorisée
"""

import os
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from mongo import client, use_fallback, db, collection
from config import config
import sqlite3
import pickle
from sklearn.metrics.pairwise import cosine_similarity


class SemanticSearch:
    """Classe pour effectuer des recherches sémantiques"""
    
    def __init__(self):
        """Initialise le modèle d'embedding et la connexion DB"""
        print(f"Chargement du modèle d'embedding: {config.embedding_model}")
        self.model = SentenceTransformer(config.embedding_model)
        self.use_fallback = use_fallback
        
    def generate_query_embedding(self, query: str) -> List[float]:
        """Génère l'embedding pour une requête"""
        return self.model.encode(query).tolist()
    
    def search_mongodb(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Recherche dans MongoDB en utilisant la similarité cosinus"""
        # MongoDB ne support pas nativement la recherche vectorielle
        # On récupère tous les documents et calcule la similarité côté client
        all_docs = list(collection.find({}, {"filename": 1, "content": 1, "embedding": 1, "chunk_index": 1}))
        
        if not all_docs:
            return []
        
        # Calcul des similarités
        similarities = []
        query_vector = np.array(query_embedding).reshape(1, -1)
        
        for doc in all_docs:
            doc_vector = np.array(doc['embedding']).reshape(1, -1)
            similarity = cosine_similarity(query_vector, doc_vector)[0][0]
            
            # Format standardisé pour la compatibilité avec search_sqlite
            similarities.append({
                'document': {
                    'id': str(doc['_id']),
                    'filename': doc['filename'],
                    'content': doc['content'],
                    'chunk_index': doc.get('chunk_index', 0)
                },
                'similarity': similarity
            })
        
        # Tri par similarité décroissante
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def search_sqlite(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Recherche dans SQLite en utilisant la similarité cosinus"""
        cursor = db.cursor()
        cursor.execute('SELECT id, filename, content, embedding, chunk_index FROM docs')
        all_docs = cursor.fetchall()
        
        if not all_docs:
            return []
        
        # Calcul des similarités
        similarities = []
        query_vector = np.array(query_embedding).reshape(1, -1)
        
        for doc in all_docs:
            doc_embedding = pickle.loads(doc[3])  # embedding est en position 3
            doc_vector = np.array(doc_embedding).reshape(1, -1)
            similarity = cosine_similarity(query_vector, doc_vector)[0][0]
            
            similarities.append({
                'document': {
                    'id': doc[0],
                    'filename': doc[1],
                    'content': doc[2],
                    'chunk_index': doc[4]
                },
                'similarity': similarity
            })
        
        # Tri par similarité décroissante
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Effectue une recherche sémantique
        
        Args:
            query: Texte de la requête
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste des résultats avec leur score de similarité
        """
        print(f"🔍 Recherche: '{query}'")
        print(f"📊 Mode: {'SQLite' if self.use_fallback else 'MongoDB'}")
        
        # Génération de l'embedding de la requête
        query_embedding = self.generate_query_embedding(query)
        
        # Recherche selon la base de données
        if self.use_fallback:
            results = self.search_sqlite(query_embedding, top_k)
        else:
            results = self.search_mongodb(query_embedding, top_k)
        
        return results
    
    def format_results(self, results: List[Dict]) -> str:
        """Formate les résultats pour l'affichage"""
        if not results:
            return "❌ Aucun résultat trouvé"
        
        output = []
        output.append(f"📋 {len(results)} résultat(s) trouvé(s):\n")
        
        for i, result in enumerate(results, 1):
            doc = result['document']
            similarity = result['similarity']
            
            output.append(f"🔸 Résultat {i} (similarité: {similarity:.4f})")
            output.append(f"   📄 Fichier: {doc['filename']}")
            if 'chunk_index' in doc:
                output.append(f"   📑 Chunk: {doc['chunk_index']}")
            output.append(f"   📝 Contenu: {doc['content'][:200]}...")
            output.append("")
        
        return "\n".join(output)


def interactive_search():
    """Interface interactive pour tester la recherche"""
    search_engine = SemanticSearch()
    
    print("=" * 60)
    print("🔍 RECHERCHE SÉMANTIQUE INTERACTIVE")
    print("=" * 60)
    print("Entrez vos requêtes (tapez 'quit' pour quitter)")
    print("-" * 60)
    
    while True:
        try:
            query = input("\n🔍 Recherche: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir !")
                break
            
            if not query:
                continue
            
            # Effectuer la recherche
            results = search_engine.search(query, top_k=3)
            
            # Afficher les résultats
            formatted_results = search_engine.format_results(results)
            print(formatted_results)
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")


def test_search_examples():
    """Teste la recherche avec des exemples prédéfinis"""
    search_engine = SemanticSearch()
    
    test_queries = [
        "Quels sont les droits du consommateur?",
        "Comment fonctionne un contrat de travail?",
        "Propriété intellectuelle et brevets",
        "Procédure judiciaire et tribunaux"
    ]
    
    print("=" * 60)
    print("🧪 TEST DE RECHERCHE AVEC EXEMPLES")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n{'='*50}")
        results = search_engine.search(query, top_k=2)
        formatted_results = search_engine.format_results(results)
        print(formatted_results)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_search_examples()
    else:
        interactive_search()
