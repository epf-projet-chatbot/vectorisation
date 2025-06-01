"""
Configuration pour la pipeline de vectorisation
"""

import os
from dataclasses import dataclass

@dataclass
class VectorizationConfig:
    """Configuration pour la vectorisation"""
    
    # Paramètres de chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Configuration MongoDB
    mongo_url: str = "mongodb://admin:password@localhost:27017"
    database_name: str = "chatbot-files"
    collection_name: str = "docs"
    
    # Configuration des données
    data_dir: str = "./data"
    markdown_subdir: str = "kiwiXlegal"
    pdf_subdir: str = "root"
    
    # Configuration du modèle d'embedding
    embedding_model: str = "intfloat/multilingual-e5-small"
    
    @classmethod
    def from_env(cls):
        """Crée une configuration à partir des variables d'environnement"""
        return cls(
            chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 200)),
            mongo_url=os.getenv("MONGO_URL", "mongodb://localhost:27017"),
            database_name=os.getenv("DATABASE_NAME", "chatbot-files"),
            collection_name=os.getenv("COLLECTION_NAME", "docs"),
            data_dir=os.getenv("DATA_DIR", "./data"),
            markdown_subdir=os.getenv("MARKDOWN_SUBDIR", "kiwiXlegal"),
            pdf_subdir=os.getenv("PDF_SUBDIR", "root"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
        )

# Configuration globale
config = VectorizationConfig.from_env()
