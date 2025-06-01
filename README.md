# Pipeline de Vectorisation

Ce module contient une pipeline complète pour traiter des documents, les découper en chunks, générer leurs embeddings et les stocker dans MongoDB.

## Architecture

```
vectorisation/
├── pipeline.py          # Point d'entrée principal - orchestre toute la pipeline
├── loader.py           # Chargement des documents (PDF, Markdown, JSON)
├── chunker.py          # Découpage des documents en chunks
├── embedder.py         # Génération des embeddings
├── mongo.py            # Interface avec MongoDB
├── config.py           # Configuration centralisée
└── requirements.txt    # Dépendances Python
```

## Utilisation

### Lancement de la pipeline complète

```bash
# Activation de l'environnement virtuel
source env/bin/activate

# Lancement avec les paramètres par défaut
python pipeline.py

# Lancement avec des paramètres personnalisés
python pipeline.py --chunk-size 1500 --overlap 300

# Nettoyage de la base avant insertion
python pipeline.py --clear-db

# Afficher uniquement les statistiques
python pipeline.py --stats-only
```

### Options disponibles

- `--chunk-size`: Taille maximale des chunks en caractères (défaut: 1000)
- `--overlap`: Chevauchement entre chunks en caractères (défaut: 200)
- `--clear-db`: Vide la base de données avant l'insertion
- `--stats-only`: Affiche uniquement les statistiques de la DB

## Étapes de la pipeline

1. **Chargement des documents** (`loader.py`)
   - Charge les fichiers Markdown du dossier `data/kiwiXlegal/`
   - Charge les fichiers PDF du dossier `data/root/` (récursivement)
   - Charge le fichier JSON du dossier `data/`

2. **Découpage en chunks** (`chunker.py`)
   - Découpe les documents en petits chunks
   - Préserve le contexte avec un chevauchement
   - Coupe intelligemment aux points de ponctuation

3. **Génération des embeddings** (`embedder.py`)
   - Utilise le modèle `intfloat/multilingual-e5-small`
   - Génère un vecteur d'embedding pour chaque chunk

[![Model on HF](https://huggingface.co/datasets/huggingface/badges/resolve/main/model-on-hf-sm-dark.svg)](https://huggingface.co/models)

4. **Stockage dans MongoDB** (`mongo.py`)
   - Insère les chunks avec leurs embeddings
   - Préserve les métadonnées (source, index du chunk, etc.)

## Configuration

La configuration peut être modifiée via des variables d'environnement :

```bash
export CHUNK_SIZE=1500
export CHUNK_OVERLAP=300
export MONGO_URL="mongodb://localhost:27017"
export DATABASE_NAME="chatbot-files"
export COLLECTION_NAME="docs"
```

## Structure des données en base

Chaque document dans MongoDB a la structure suivante :

```json
{
  "filename": "path/to/source/file.pdf",
  "content": "Contenu du chunk...",
  "embedding": [0.1, 0.2, 0.3, ...],
  "chunk_index": 0,
  "total_chunks": 5
}
```

## Prérequis

- Python 3.8+
- MongoDB en cours d'exécution
- Dossier `data/` avec les documents à traiter

## Installation des dépendances

```bash
pip install -r requirements.txt
```