"""
Module de connexion et d'opérations MongoDB pour la vectorisation
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from typing import List, Dict
from tqdm import tqdm
from config import config

# Variables globales pour la connexion MongoDB
client = None
db = None
collection = None

def init_connection():
    """Initialise la connexion à MongoDB"""
    global client, db, collection
    
    try:
        # Connexion à MongoDB
        client = MongoClient(config.mongo_url, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Test de connexion
        
        # Utiliser les méthodes de configuration pour obtenir les bons noms
        database_name = config.get_database_name()
        collection_name = config.get_collection_name()
        
        db = client[database_name]
        collection = db[collection_name]
        
        mode_info = "MODE TEST" if config.test_mode else "MODE PRODUCTION"
        print(f"✅ Connexion MongoDB établie ({mode_info})")
        print(f"📊 Base: {database_name}, Collection: {collection_name}")
        return True
    except (ServerSelectionTimeoutError, OperationFailure) as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        raise ConnectionError(f"Impossible de se connecter à MongoDB: {e}")
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        raise

def insert_chunks_batch(chunks_data: List[Dict], batch_size: int = None):
    """
    Insère les chunks dans MongoDB par lots
    
    Args:
        chunks_data: Liste des chunks avec leurs métadonnées et embeddings
        batch_size: Taille des lots (par défaut utilise config.batch_size)
    """
    if not chunks_data:
        print("Aucun chunk à insérer")
        return
    
    if batch_size is None:
        batch_size = config.batch_size
    
    print(f"Insertion de {len(chunks_data)} chunks en lots de {batch_size}")
    
    # Vérifier la connexion
    if collection is None:
        raise ConnectionError("Connexion MongoDB non initialisée")
    
    total_inserted = 0
    
    # Insertion par lots
    for i in tqdm(range(0, len(chunks_data), batch_size), desc="Insertion des chunks"):
        batch = chunks_data[i:i + batch_size]
        
        try:
            result = collection.insert_many(batch)
            total_inserted += len(result.inserted_ids)
        except Exception as e:
            print(f"Erreur lors de l'insertion du lot {i//batch_size + 1}: {e}")
            raise
    
    print(f"{total_inserted} chunks insérés avec succès dans MongoDB")

def count_documents() -> int:
    """Retourne le nombre de documents dans la collection"""
    if collection is None:
        raise ConnectionError("Connexion MongoDB non initialisée")
    
    return collection.count_documents({})

def get_collection_stats() -> Dict:
    """Retourne des statistiques sur la collection"""
    if collection is None:
        raise ConnectionError("Connexion MongoDB non initialisée")
    
    stats = {
        'total_documents': collection.count_documents({}),
        'unique_files': len(collection.distinct('filename')),
        'database_name': config.get_database_name(),
        'collection_name': config.get_collection_name(),
        'test_mode': config.test_mode
    }
    
    # Statistiques par type de fichier
    file_types = {}
    filenames = collection.distinct('filename')
    for filename in filenames:
        ext = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
        file_types[ext] = file_types.get(ext, 0) + 1
    
    stats['file_types'] = file_types
    
    return stats

def clear_collection():
    """Vide la collection (utile pour les tests)"""
    if collection is None:
        raise ConnectionError("Connexion MongoDB non initialisée")
    
    result = collection.delete_many({})
    print(f"{result.deleted_count} documents supprimés de la collection")
    return result.deleted_count

def test_connection() -> bool:
    """
    Teste la connexion à MongoDB
    
    Returns:
        True si la connexion fonctionne, False sinon
    """
    try:
        if client is None:
            return False
        
        # Test simple de ping
        client.admin.command('ping')
        return True
    except Exception:
        return False

def close_connection():
    """Ferme la connexion MongoDB"""
    global client
    if client:
        client.close()
        print("Connexion MongoDB fermée")

# Initialisation automatique de la connexion
try:
    init_connection()
except Exception as e:
    print(f"Impossible d'initialiser la connexion MongoDB: {e}")
    raise
