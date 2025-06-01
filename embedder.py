from sentence_transformers import SentenceTransformer
from typing import List, Dict
from tqdm import tqdm

# Charger le modèle une seule fois
model = SentenceTransformer("intfloat/multilingual-e5-small")

def get_embedding(text: str) -> List[float]:
    """
    Génère l'embedding d'un texte
    
    Args:
        text: Le texte à vectoriser
        
    Returns:
        Liste des valeurs de l'embedding
    """
    return model.encode(text).tolist()

def process_chunks_embeddings(chunks: List[Dict]) -> List[Dict]:
    """
    Génère les embeddings pour tous les chunks
    
    Args:
        chunks: Liste des chunks de documents
        
    Returns:
        Liste des chunks avec leurs embeddings
    """
    print(f"Génération des embeddings pour {len(chunks)} chunks...")
    
    processed_chunks = []
    
    for chunk in tqdm(chunks, desc="Embedding"):
        embedding = get_embedding(chunk['content'])
        chunk_with_embedding = chunk.copy()
        chunk_with_embedding['embedding'] = embedding
        processed_chunks.append(chunk_with_embedding)
    
    print(f"✓ {len(processed_chunks)} embeddings générés")
    return processed_chunks