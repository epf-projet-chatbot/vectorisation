from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from typing import List, Dict
from tqdm import tqdm
import os
import json
import sqlite3
import pickle

# Configuration MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://admin:password@localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "chatbot-files")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "docs")

# Variables globales pour la connexion
client = None
db = None
collection = None
use_fallback = False

def init_connection():
    """Initialise la connexion à MongoDB avec fallback sur SQLite"""
    global client, db, collection, use_fallback
    
    try:
        # Test de connexion MongoDB
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Test de connexion
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        print("✅ Connexion MongoDB établie")
        use_fallback = False
        return True
    except (ServerSelectionTimeoutError, OperationFailure) as e:
        print(f"⚠️  MongoDB non disponible ({e}), utilisation de SQLite comme fallback")
        use_fallback = True
        _init_sqlite_fallback()
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("Utilisation de SQLite comme fallback")
        use_fallback = True
        _init_sqlite_fallback()
        return True

def _init_sqlite_fallback():
    """Initialise SQLite comme base de données de fallback"""
    global db
    db = sqlite3.connect('vectorisation_fallback.db')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            content TEXT,
            embedding BLOB,
            chunk_index INTEGER,
            total_chunks INTEGER
        )
    ''')
    db.commit()
    print("✅ Base SQLite initialisée comme fallback")

# Initialisation automatique
init_connection()

def insert_document(filename: str, content: str, embedding: List[float], chunk_index: int = 0, total_chunks: int = 1):
    """
    Insère un document dans MongoDB
    
    Args:
        filename: Nom du fichier source
        content: Contenu du chunk
        embedding: Vecteur d'embedding
        chunk_index: Index du chunk dans le document
        total_chunks: Nombre total de chunks du document
    """
    document = {
        "filename": filename,
        "content": content,
        "embedding": embedding,
        "chunk_index": chunk_index,
        "total_chunks": total_chunks
    }
    
    result = collection.insert_one(document)
    return result.inserted_id

def insert_chunks_batch(chunks: List[Dict], batch_size: int = 1000) -> List[str]:
    """
    Insère une liste de chunks dans MongoDB en lots de taille contrôlée
    
    Args:
        chunks: Liste des chunks avec embeddings
        batch_size: Taille de chaque lot pour l'insertion (défaut: 1000)
        
    Returns:
        Liste des IDs des documents insérés
    """
    if use_fallback:
        return _insert_chunks_sqlite(chunks)
    
    print(f"Insertion de {len(chunks)} chunks dans MongoDB par lots de {batch_size}...")
    
    all_inserted_ids = []
    total_chunks = len(chunks)
    
    # Traitement par lots pour éviter les timeouts
    for i in tqdm(range(0, total_chunks, batch_size), desc="Insertion dans MongoDB"):
        batch_chunks = chunks[i:i + batch_size]
        
        documents = []
        for chunk in batch_chunks:
            document = {
                "filename": chunk['source'],
                "content": chunk['content'],
                "embedding": chunk['embedding'],
                "chunk_index": chunk.get('chunk_index', 0),
                "total_chunks": chunk.get('total_chunks', 1)
            }
            documents.append(document)
        
        try:
            # Insertion du lot courant
            result = collection.insert_many(documents, ordered=False)
            batch_ids = [str(id) for id in result.inserted_ids]
            all_inserted_ids.extend(batch_ids)
            
            print(f"  ✓ Lot {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}: {len(batch_ids)} documents insérés")
            
        except Exception as e:
            print(f"  ❌ Erreur lors de l'insertion du lot {i//batch_size + 1}: {e}")
            # Continue avec le lot suivant même en cas d'erreur
            continue
    
    print(f"✅ {len(all_inserted_ids)} chunks insérés au total dans MongoDB")
    return all_inserted_ids

def _insert_chunks_sqlite(chunks: List[Dict]) -> List[str]:
    """Insère les chunks dans SQLite comme fallback"""
    print(f"Insertion de {len(chunks)} chunks dans SQLite (fallback)...")
    
    cursor = db.cursor()
    inserted_ids = []
    
    for chunk in tqdm(chunks, desc="Insertion SQLite"):
        cursor.execute('''
            INSERT INTO docs (filename, content, embedding, chunk_index, total_chunks)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            chunk['source'],
            chunk['content'],
            pickle.dumps(chunk['embedding']),  # Sérialisation de l'embedding
            chunk.get('chunk_index', 0),
            chunk.get('total_chunks', 1)
        ))
        inserted_ids.append(str(cursor.lastrowid))
    
    db.commit()
    print(f"✅ {len(inserted_ids)} chunks insérés dans SQLite")
    return inserted_ids

def clear_collection():
    """Vide la collection (utile pour les tests)"""
    if use_fallback:
        cursor = db.cursor()
        cursor.execute('DELETE FROM docs')
        db.commit()
        print(f"✓ Base SQLite vidée")
    else:
        result = collection.delete_many({})
        print(f"✓ {result.deleted_count} documents supprimés de la collection MongoDB")

def get_collection_stats():
    """Affiche les statistiques de la collection"""
    if use_fallback:
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM docs')
        count = cursor.fetchone()[0]
        print(f"Base SQLite contient {count} documents")
    else:
        count = collection.count_documents({})
        print(f"Collection '{COLLECTION_NAME}' contient {count} documents")
    return count

def test_connection():
    """Teste la connexion et affiche les informations"""
    global client, db, collection, use_fallback
    
    if use_fallback:
        print("❌ Utilisation du fallback SQLite - MongoDB non disponible")
        return False
    
    try:
        # Test ping
        client.admin.command('ping')
        
        # Informations sur la base
        db_list = client.list_database_names()
        print(f"✅ Connexion MongoDB active")
        print(f"📊 Bases de données disponibles: {db_list}")
        
        # Informations sur la collection
        collections = db.list_collection_names()
        print(f"📁 Collections dans '{DATABASE_NAME}': {collections}")
        
        if COLLECTION_NAME in collections:
            count = collection.count_documents({})
            print(f"📄 Documents dans '{COLLECTION_NAME}': {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return False