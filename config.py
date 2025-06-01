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
    mongo_url: str = "mongodb://localhost:27018"
    database_name: str = "chatbot-files"
    collection_name: str = "docs"
    
    # Configuration des données
    data_dir: str = "./data"
    markdown_subdir: str = "kiwiXlegal"
    pdf_subdir: str = "root"
    json_filename: str = "all_aos.json"
    
    # Mode test avec données réduites
    test_mode: bool = False
    test_data_dir: str = "./data_test"
    test_json_filename: str = "all_aos_sample.json"
    
    # Configuration du modèle d'embedding
    embedding_model: str = "intfloat/multilingual-e5-small"
    
    # Taille des lots pour l'insertion MongoDB
    batch_size: int = 500
    
    def get_data_dir(self) -> str:
        """Retourne le répertoire de données selon le mode"""
        return self.test_data_dir if self.test_mode else self.data_dir
    
    def get_json_filename(self) -> str:
        """Retourne le nom du fichier JSON selon le mode"""
        return self.test_json_filename if self.test_mode else self.json_filename

    @classmethod
    def from_env(cls):
        """Crée une configuration à partir des variables d'environnement"""
        return cls(
            chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 200)),
            mongo_url=os.getenv("MONGO_URL", "mongodb://localhost:27018"),
            database_name=os.getenv("DATABASE_NAME", "chatbot-files"),
            collection_name=os.getenv("COLLECTION_NAME", "docs"),
            data_dir=os.getenv("DATA_DIR", "./data"),
            markdown_subdir=os.getenv("MARKDOWN_SUBDIR", "kiwiXlegal"),
            pdf_subdir=os.getenv("PDF_SUBDIR", "root"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small"),
            test_mode=os.getenv("TEST_MODE", "False").lower() in ["true", "1"],
            test_data_dir=os.getenv("TEST_DATA_DIR", "./data_test"),
            test_json_filename=os.getenv("TEST_JSON_FILENAME", "all_aos_sample.json"),
            batch_size=int(os.getenv("BATCH_SIZE", 500))
        )

# Configuration globale
config = VectorizationConfig.from_env()
