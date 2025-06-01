import re
from typing import List, Dict

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Découpe un texte en chunks avec un chevauchement
    
    Args:
        text: Le texte à découper
        chunk_size: Taille maximale de chaque chunk en caractères
        overlap: Nombre de caractères de chevauchement entre les chunks
    
    Returns:
        Liste des chunks de texte
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculer la fin du chunk
        end = min(start + chunk_size, len(text))
        
        # Si ce n'est pas le dernier chunk, essayer de couper à un point naturel
        if end < len(text):
            # Chercher le dernier point, point d'exclamation ou point d'interrogation
            last_sentence_end = max(
                text.rfind('.', start, end),
                text.rfind('!', start, end),
                text.rfind('?', start, end)
            )
            
            # Si on trouve un point de coupure naturel, l'utiliser
            if last_sentence_end > start:
                end = last_sentence_end + 1
            else:
                # Sinon, chercher le dernier espace
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
        
        # Extraire le chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Calculer le prochain point de départ avec chevauchement
        if end >= len(text):
            break
            
        start = max(start + 1, end - overlap)
    
    return chunks

def split_document_into_chunks(document: Dict, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Découpe un document en chunks
    
    Args:
        document: Document avec 'source' et 'content'
        chunk_size: Taille maximale de chaque chunk
        overlap: Chevauchement entre chunks
    
    Returns:
        Liste de chunks avec métadonnées
    """
    chunks = split_text_into_chunks(document['content'], chunk_size, overlap)
    
    result = []
    for i, chunk_text in enumerate(chunks):
        chunk_doc = {
            'source': document['source'],
            'content': chunk_text,
            'chunk_index': i,
            'total_chunks': len(chunks)
        }
        result.append(chunk_doc)
    
    return result

def process_documents_chunks(documents: List[Dict], chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Traite une liste de documents et les découpe en chunks
    
    Args:
        documents: Liste de documents
        chunk_size: Taille maximale de chaque chunk
        overlap: Chevauchement entre chunks
    
    Returns:
        Liste de tous les chunks de tous les documents
    """
    all_chunks = []
    
    print(f"Découpage de {len(documents)} documents en chunks...")
    
    for doc in documents:
        doc_chunks = split_document_into_chunks(doc, chunk_size, overlap)
        all_chunks.extend(doc_chunks)
    
    print(f"✓ {len(all_chunks)} chunks créés")
    return all_chunks
