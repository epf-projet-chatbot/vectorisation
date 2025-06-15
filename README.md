# Pipeline de Vectorisation pour Chatbot Juridique

## Vue d'ensemble

Cette pipeline traite des documents juridiques (Markdown, PDF, JSON) pour créer une base de données vectorisée. Le système utilise MongoDB pour le stockage et génère des embeddings en français pour chaque chunk de document.

## Architecture

```
Documents Sources
    ├── Markdown (.md) - Articles juridiques
    ├── PDF - Documents officiels
    └── JSON - Données structurées (AOS)
         ↓
Pipeline de Traitement
    ├── 1. Chargement des documents
    ├── 2. Découpage en chunks (1000 chars, overlap 200)
    ├── 3. Génération embeddings (multilingual-e5-small)
    └── 4. Insertion MongoDB (par lots de 500)
         ↓
Base de Données MongoDB
    └── Collection: docs {filename, content, embedding, chunk_index}
```

## Installation

```bash
# Aller dans le dossier vectorisation
cd /path/to/vectorisation

# Créer un environnement virtuel
python3 -m venv env
source env/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer NLTK (nécessaire pour le chunker avancé)
python setup_nltk.py

# Démarrer MongoDB (mode test sur port 27017)
mongod --config /usr/local/etc/mongod_test.conf --noauth
```

## Modes d'utilisation

### Mode Test (Recommandé pour débuter)

Utilise un dataset réduit pour les tests et le développement :
- **7 fichiers** : 3 Markdown + 3 PDF + 1 JSON
- **~230 chunks** générés
- **Données** : `./data_test/`

```bash
# Lancer la pipeline en mode test
python pipeline.py --test

# Lancer la pipeline test avec nettoyage de la DB
python pipeline.py --test --clear-db
```

### Mode Production

Traite l'ensemble des documents du projet :
- **100+ fichiers** (volume complet)
- **Données** : `./data/`

```bash
# Lancer la pipeline en production
python pipeline.py

# Avec paramètres personnalisés
python pipeline.py --chunk-size 1500 --overlap 300 --clear-db
```

### Statistiques uniquement

```bash
python pipeline.py --stats-only
```

## Configuration

Le fichier `config.py` centralise tous les paramètres :

```python
# Configuration MongoDB
mongo_url: str = "mongodb://localhost:27017"
database_name: str = "chatbot_db"
collection_name: str = "docs"

# Paramètres de chunking
chunk_size: int = 1000
chunk_overlap: int = 200

# Modèle d'embedding
embedding_model: str = "intfloat/multilingual-e5-small"

# Taille des lots pour MongoDB
batch_size: int = 500

# Mode test/production
test_mode: bool = False  # Basculé automatiquement par --test
```

## Structure des Données

### Mode Test (`./data_test/`)
```
data_test/
├── kiwiXlegal/
│   ├── _111.md
│   ├── _112.md
│   └── _article-categories_changements-legaux_page_2_113.md
├── root/
│   ├── Analyse des litiges, problématiques et recommandations - 2023-2024 - Chiffres Principaux.pdf
│   ├── Arrêté Ministériel (1988).pdf
│   └── Lettre de l'ACOSS (2007).pdf
└── all_aos_sample.json
```

### Mode Production (`./data/`)
```
data/
├── kiwiXlegal/          # Articles juridiques (Markdown)
├── root/                # Documents PDF
└── all_aos.json         # Données complètes AOS
```

## Tests et Validation

### Test PDF Processing
```bash
python test_pdf.py
```

### Test JSON Processing
```bash
python test_json.py
```

## Scripts Utilitaires

| Script | Description |
|--------|-------------|
| `pipeline.py` | Pipeline principale de traitement |
| `config.py` | Configuration centralisée |
| `loader.py` | Chargement des documents |
| `chunker.py` | Découpage en chunks |
| `embedder.py` | Génération des embeddings |
| `mongo.py` | Opérations MongoDB |
| `test_pdf.py` | Tests pour le traitement PDF |
| `test_json.py` | Tests pour le traitement JSON |

## 📋 Exemples d'Usage

### 1. Premier Démarrage (Mode Test)
```bash
# Activer l'environnement virtuel
source env/bin/activate

# Nettoyage et traitement des données test
python pipeline.py --test --clear-db

# Vérification des statistiques
python pipeline.py --stats-only
```

### 2. Mise en Production
```bash
# Traitement des données complètes
python pipeline.py --clear-db

# Vérification du résultat
python pipeline.py --stats-only
```

### 3. Mise à Jour Incrémentale
```bash
# Sans nettoyage (ajoute aux données existantes)
python pipeline.py --test
```

### 4. Tests de Validation
```bash
# Test du traitement PDF
python test_pdf.py

# Test du traitement JSON
python test_json.py

# Démonstration d'accès aux données
python demo_access.py
```

## Performances

### Mode Test (7 fichiers)
- **Traitement** : ~30 secondes
- **Chunks** : 229
- **Documents MongoDB** : 229

### Mode Production (Estimé)
- **Traitement** : ~10-15 minutes
- **Chunks** : ~5000-10000
- **Documents MongoDB** : ~5000-10000

## 🔄 Format des Données Stockées

Chaque document dans MongoDB contient :
```json
{
  "_id": "ObjectId",
  "filename": "./data_test/kiwiXlegal/_112.md",
  "content": "Contenu du chunk...",
  "embedding": [0.123, -0.456, ...],  // Vecteur 384 dimensions
  "chunk_index": 0,
  "total_chunks": 8
}
```

## 🚨 Dépannage

### MongoDB non démarré
```bash
# Vérifier le statut
ps aux | grep mongod

# Démarrer MongoDB test
mongod --config /usr/local/etc/mongod_test.conf --noauth
```

### Erreur de mémoire
```bash
# Réduire la taille des lots
export BATCH_SIZE=250
python pipeline.py --test
```

### Réinitialisation complète
```bash
# Supprimer toutes les données
python pipeline.py --test --clear-db
```

## 🔄 Variables d'Environnement

```bash
# Configuration MongoDB
export MONGO_URL="mongodb://localhost:27017"
export DATABASE_NAME="chatbot_db"
export COLLECTION_NAME="docs"

# Paramètres de chunking
export CHUNK_SIZE=1000
export CHUNK_OVERLAP=200

# Mode test
export TEST_MODE=true
```

## Métriques et Monitoring

Le système fournit automatiquement :
- Nombre de documents traités
- Nombre de chunks générés  
- Temps de traitement par étape
- Statistiques de la base de données
- Scores de similarité pour la recherche

## 🔗 Intégration avec le Chatbot

### Accès aux Données Vectorisées

Pour utiliser les données vectorisées dans votre application :

```python
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["chatbot_db"]
collection = db["docs"]

# Récupérer tous les documents
documents = list(collection.find({}, {"filename": 1, "content": 1, "embedding": 1}))

# Exemple : Recherche par nom de fichier
pdf_docs = list(collection.find({"filename": {"$regex": "\.pdf$"}}))
```

### Utilisation des Embeddings

Les embeddings générés (vecteurs de 384 dimensions) peuvent être utilisés pour :
- Recherche par similarité sémantique
- Classification automatique de documents
- Recommandation de contenu similaire
- Analyse de clustering de documents

---

**🎯 Objectif** : Cette pipeline prépare les données pour un système de chatbot en générant des embeddings vectoriels stockés dans MongoDB. Les données vectorisées peuvent ensuite être utilisées par d'autres composants du système pour la recherche sémantique et la génération de réponses.