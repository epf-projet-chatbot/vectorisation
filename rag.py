from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from os import getenv
import os
from sklearn.neighbors import NearestNeighbors
from embedder import get_embedding

client = None
db = os.getenv('DATABASE_NAME')
collection = os.getenv('COLLECTION_NAME')

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
        Une liste des identifiants des k vecteurs les plus proches.
    """
    global client, db, collection
    
    if client is None:
        try:
            client = MongoClient(os.getenv('MONGO_URL'), serverSelectionTimeoutMS=5000)
            client.admin.command('ping')  # Test de connexion
            print("Connexion MongoDB établie")
        except (ServerSelectionTimeoutError, OperationFailure) as e:
            print(f"Erreur de connexion MongoDB: {e}")
            raise ConnectionError(f"Impossible de se connecter à MongoDB: {e}")
    
    if db is None or collection is None:
        raise ValueError("Nom de la base de données ou de la collection non défini.")
    
    # Récupérer tous les vecteurs et leurs métadonnées
    vectors = list(client[db][collection].find())
    
    if not vectors:
        return []
    
    # Extraire les vecteurs du champ embedding
    vector_data = [v['embedding'] for v in vectors]
    
    # Utiliser NearestNeighbors pour trouver les k plus proches voisins
    nbrs = NearestNeighbors(n_neighbors=k, algorithm='auto').fit(vector_data)
    distances, indices = nbrs.kneighbors([request_vector])
    
    # Récupérer le contexte associé à ces vecteurs
    closest_vectors = [vectors[i] for i in indices[0]]
    context_texts = [v['content'] for v in closest_vectors]
    
    return context_texts