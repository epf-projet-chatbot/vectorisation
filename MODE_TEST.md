# Mode Test/Production pour le RAG

## Description

Le système RAG supporte deux modes :

- **Mode PRODUCTION** : Utilise la base `chatbot_db` avec toutes les données
- **Mode TEST** : Utilise la base `chatbot_test_db` avec des données de test

## Utilisation par arguments de ligne de commande

### 1. Pipeline de vectorisation

```bash
# Mode TEST (données réduites)
python3 pipeline.py --test

# Mode PRODUCTION (toutes les données)
python3 pipeline.py
python3 pipeline.py --prod

# Options supplémentaires
python3 pipeline.py --test --clear-db    # Vide la base de test avant
python3 pipeline.py --stats-only         # Affiche uniquement les stats
```

### 2. Tests de performance

```bash
# Mode TEST
python3 rag_performance_test.py --test

# Mode PRODUCTION  
python3 rag_performance_test.py
python3 rag_performance_test.py --prod
```

## 🔧 Configuration

### Variables d'environnement (fichier .env)

```bash
# Bases de données
DATABASE_NAME=chatbot_db              # Base de production
COLLECTION_NAME=data                  # Collection de production

# Mode test
TEST_MODE=false                       # true pour activer le mode test
TEST_DATABASE_NAME=chatbot_test_db   # Base de test
TEST_COLLECTION_NAME=data             # Collection de test

# Données
DATA_DIR=./data                       # Données de production
TEST_DATA_DIR=./data_clean/cleaned_output            # Données de test
TEST_JSON_FILENAME=all_aos_sample.json
```

## 🔄 Autres méthodes de basculement

### 1. Script de basculement

```bash
python3 switch_mode.py toggle    # Bascule le mode
python3 switch_mode.py show      # Affiche le mode actuel
```

### 2. Interface de test

```bash
python3 rag_performance_test.py
# Choisir l'option 7 "Basculer entre mode TEST/PRODUCTION"
```

### 3. Modification manuelle

Éditer le fichier `.env` :
```bash
TEST_MODE=true   # Pour le mode test
TEST_MODE=false  # Pour le mode production
```

## ⚠️ Important

- Les **arguments en ligne de commande** (`--test`, `--prod`) ont la **priorité** sur le fichier .env
- Les deux bases de données doivent être **vectorisées séparément**
