from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from os import getenv
import os
from sklearn.neighbors import NearestNeighbors
from embedder import get_embedding
from mongo import init_connection, client, db, collection
from config import config

def make_vector(user_request:str):
    """
    Transforme la requête utilisateur en vecteur.
    
    Args:
        user_request: La requête de l'utilisateur à transformer en vecteur.
    
    Returns:
        Un vecteur représentant la requête de l'utilisateur.
    """
    
    return get_embedding(user_request)

def k_context_vectors(request_vector, k:int):
    """
    Récupère les k vecteurs les plus proches du vecteur de requête dans la collection MongoDB.
    
    Args:
        request_vector: Le vecteur de requête pour la recherche.
        k: Le nombre de vecteurs à récupérer.
    
    Returns:
        Une liste du contenu des k documents les plus proches.
    """
    # S'assurer que la connexion est initialisée
    init_connection()
    
    # Vérifier que la collection est disponible
    if collection is None:
        raise ConnectionError("Collection MongoDB non initialisée")
    
    # Récupérer tous les vecteurs et leurs métadonnées
    vectors = list(collection.find())
    
    # Afficher des informations de debug avec les bons noms de base/collection
    database_name = config.get_database_name()
    collection_name = config.get_collection_name()
    mode_info = "TEST" if config.test_mode else "PROD"
    
    print(f"📊 [{mode_info}] {len(vectors)} vecteurs dans '{database_name}.{collection_name}'")
    
    if not vectors:
        print("⚠️  Aucun vecteur trouvé dans la collection.")
        return []
    
    # Extraire les vecteurs du champ embedding
    vector_data = [v['embedding'] for v in vectors]
    
    # Utiliser NearestNeighbors pour trouver les k plus proches voisins
    # S'assurer que k ne dépasse pas le nombre de vecteurs disponibles
    effective_k = min(k, len(vectors))
    nbrs = NearestNeighbors(n_neighbors=effective_k, algorithm='auto').fit(vector_data)
    distances, indices = nbrs.kneighbors([request_vector])
    
    # Récupérer le contexte associé à ces vecteurs
    closest_vectors = [vectors[i] for i in indices[0]]
    
    # Trier par pertinence (distance croissante) et ajouter les distances
    vector_with_distance = list(zip(closest_vectors, distances[0]))
    vector_with_distance.sort(key=lambda x: x[1])  # Trier par distance croissante
    
    # Extraire le contenu et filtrer les doublons
    context_texts = []
    seen_content = set()
    
    for vector, distance in vector_with_distance:
        content = vector['content']
        # Éviter les doublons de contenu
        content_hash = hash(content[:100])  # Hash des 100 premiers caractères
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            context_texts.append(content)
    
    print(f"✅ {len(context_texts)} chunks de contexte récupérés (doublons supprimés)")
    
    return context_texts

def k_context_vectors_smart(request_vector, k: int, prioritize_metadata: bool = True):
    """
    Version améliorée qui utilise les métadonnées pour prioriser les chunks pertinents
    
    Args:
        request_vector: Le vecteur de requête pour la recherche.
        k: Le nombre de vecteurs à récupérer.
        prioritize_metadata: Si True, privilégie les chunks avec des métadonnées importantes.
    
    Returns:
        Une liste du contenu des k documents les plus proches, optimisée par métadonnées.
    """
    # S'assurer que la connexion est initialisée
    init_connection()
    
    # Vérifier que la collection est disponible
    if collection is None:
        raise ConnectionError("Collection MongoDB non initialisée")
    
    # Récupérer tous les vecteurs et leurs métadonnées
    vectors = list(collection.find())
    
    # Afficher des informations de debug
    database_name = config.get_database_name()
    collection_name = config.get_collection_name()
    mode_info = "TEST" if config.test_mode else "PROD"
    
    print(f"📊 [{mode_info}] {len(vectors)} vecteurs dans '{database_name}.{collection_name}'")
    
    if not vectors:
        print("⚠️  Aucun vecteur trouvé dans la collection.")
        return []
    
    # Extraire les vecteurs du champ embedding
    vector_data = [v['embedding'] for v in vectors]
    
    # Utiliser NearestNeighbors pour trouver plus de voisins que nécessaire
    search_k = min(k * 3, len(vectors))  # Chercher 3x plus pour avoir du choix
    nbrs = NearestNeighbors(n_neighbors=search_k, algorithm='auto').fit(vector_data)
    distances, indices = nbrs.kneighbors([request_vector])
    
    # Récupérer les vecteurs candidats avec leurs distances
    candidates = []
    for i, distance in zip(indices[0], distances[0]):
        vector = vectors[i]
        score = 1.0 / (1.0 + distance)  # Convertir distance en score (plus haut = mieux)
        
        # Bonus pour les métadonnées importantes si activé
        if prioritize_metadata and 'metadata' in vector:
            metadata = vector['metadata']
            if metadata.get('has_numbers', False):
                score *= 1.2  # Boost pour les chunks avec des nombres
            if metadata.get('has_currency', False):
                score *= 1.3  # Boost pour les chunks avec des devises
            if metadata.get('has_dates', False):
                score *= 1.1  # Boost pour les chunks avec des dates
        
        candidates.append((vector, score, distance))
    
    # Trier par score décroissant
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Sélectionner les k meilleurs en évitant les doublons
    selected_chunks = []
    seen_content = set()
    
    for vector, score, distance in candidates:
        if len(selected_chunks) >= k:
            break
            
        content = vector['content']
        content_hash = hash(content[:100])  # Hash des 100 premiers caractères
        
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            selected_chunks.append(content)
    
    print(f"✅ {len(selected_chunks)} chunks de contexte récupérés (avec priorité métadonnées: {prioritize_metadata})")
    
    return selected_chunks