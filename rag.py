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
    print(f"Nombre de vecteurs dans la collection '{config.collection_name}': {len(vectors)}")
    
    if not vectors:
        print("Aucun vecteur trouvé dans la collection.")
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
    context_texts = [v['content'] for v in closest_vectors]
    
    print(f"✅ {len(context_texts)} chunks de contexte récupérés")
    
    return context_texts