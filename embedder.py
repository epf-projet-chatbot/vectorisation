from sentence_transformers import SentenceTransformer
from typing import List, Dict
from tqdm import tqdm
from config import config

# Charger le modèle multilingue optimisé pour le français
print(f"Chargement du modèle d'embedding: {config.embedding_model}")
model = SentenceTransformer(config.embedding_model)

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
    Génère les embeddings pour tous les chunks en utilisant le contenu prétraité
    mais en conservant le contenu original pour la base de données
    
    Args:
        chunks: Liste des chunks de documents avec 'content' (original) et 'preprocessed_content'
        
    Returns:
        Liste des chunks avec leurs embeddings et le contenu original dans 'content'
    """
    print(f"Génération des embeddings pour {len(chunks)} chunks...")
    
    processed_chunks = []
    
    for chunk in tqdm(chunks, desc="Embedding"):
        # Récupérer le contenu original et prétraité avant toute modification
        original_content = chunk.get('original_content', chunk['content'])
        preprocessed_content = chunk.get('preprocessed_content', chunk['content'])
        
        # Utiliser le contenu prétraité pour générer l'embedding
        embedding = get_embedding(preprocessed_content)
        
        # Créer le chunk final avec le contenu original et l'embedding
        chunk_with_embedding = chunk.copy()
        # S'assurer que 'content' contient le texte original NON prétraité
        chunk_with_embedding['content'] = original_content
        chunk_with_embedding['embedding'] = embedding
        
        # Nettoyer les champs temporaires
        if 'preprocessed_content' in chunk_with_embedding:
            del chunk_with_embedding['preprocessed_content']
        if 'original_content' in chunk_with_embedding:
            del chunk_with_embedding['original_content']
        
        processed_chunks.append(chunk_with_embedding)
    
    print(f"✓ {len(processed_chunks)} embeddings générés")
    return processed_chunks