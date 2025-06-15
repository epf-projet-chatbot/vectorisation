"""
🧠 ARCHITECTURE COMPLÈTE DU SYSTÈME RAG
======================================

📋 MODÈLES ET LEUR LOCALISATION :
===============================

1. 🔤 MODÈLE D'EMBEDDING (Vectorisation)
   📍 Défini dans: .env → EMBEDDING_MODEL=intfloat/multilingual-e5-small
   📍 Utilisé dans: embedder.py (ligne 8)
   🏭 Fournisseur: Hugging Face (sentence-transformers)
   📐 Dimension: 384 vecteurs
   🎯 Rôle: Convertit le texte en vecteurs numériques

2. 🤖 MODÈLE LLM (Génération de réponses)
   📍 Défini dans: rag_performance_test.py (ligne 61)
   📍 Modèle: "llama-3.3-70b-versatile"
   🏭 Fournisseur: Groq (API)
   🔑 API Key: .env → API_KEY=gsk_dzYefK...
   🎯 Rôle: Génère la réponse finale basée sur le contexte

🔄 PROCESSUS COMPLET DE VECTORISATION :
=====================================

PHASE 1: VECTORISATION INITIALE (pipeline.py)
┌─────────────────────────────────────────────────┐
│ 1. CHARGEMENT (loader.py)                      │
│    📄 PDF → texte (PyMuPDF)                   │
│    📝 Markdown → texte                         │
│    📊 JSON → texte                             │
│                                                │
│ 2. CHUNKING (chunker.py)                      │
│    📏 Taille: 1000 caractères                 │
│    🔗 Overlap: 200 caractères                 │
│                                                │
│ 3. PREPROCESSING (preprocessor.py)             │
│    🧹 Nettoyage du texte                      │
│    🔤 Normalisation                           │
│                                                │
│ 4. EMBEDDING (embedder.py)                    │
│    🧠 Modèle: intfloat/multilingual-e5-small │
│    📐 384 dimensions par chunk                 │
│                                                │
│ 5. STOCKAGE (mongo.py)                        │
│    💾 MongoDB: chatbot_test_db.data          │
│    📋 Structure: {content, embedding, source} │
└─────────────────────────────────────────────────┘

PHASE 2: REQUÊTE UTILISATEUR (rag.py + rag_performance_test.py)
┌─────────────────────────────────────────────────┐
│ 1. QUESTION UTILISATEUR                        │
│    ❓ "Quel est le nombre de litiges ?"        │
│                                                │
│ 2. VECTORISATION QUESTION (rag.py:make_vector) │
│    🧠 Même modèle: multilingual-e5-small      │
│    📐 384 dimensions                           │
│                                                │
│ 3. RECHERCHE SIMILARITÉ (rag.py:k_context)    │
│    🔍 Algorithme: NearestNeighbors (sklearn)  │
│    📊 Récupère k=5 chunks les plus proches    │
│                                                │
│ 4. GÉNÉRATION RÉPONSE (rag_performance_test)   │
│    🤖 LLM: llama-3.3-70b-versatile (Groq)    │
│    🔑 API Groq avec votre clé                 │
│    📝 Prompt + contexte → réponse             │
└─────────────────────────────────────────────────┘

🔧 CONFIGURATION DÉTAILLÉE :
===========================

📁 FICHIER .env (Configuration globale)
┌─────────────────────────────────────┐
│ EMBEDDING_MODEL=intfloat/multilingual-e5-small │
│ API_KEY=gsk_dzYefK5aUiuJmeeofFvsWG... │
│ CHUNK_SIZE=1000                     │
│ CHUNK_OVERLAP=200                   │
│ TEST_MODE=true                      │
└─────────────────────────────────────┘

📄 EMBEDDER.PY (Vectorisation)
┌─────────────────────────────────────┐
│ def get_embedding(text: str):       │
│   return model.encode(text).tolist()│
│                                     │
│ Modèle chargé ligne 8:              │
│ model = SentenceTransformer(config.embedding_model) │
└─────────────────────────────────────┘

🤖 RAG_PERFORMANCE_TEST.PY (LLM)
┌─────────────────────────────────────┐
│ client = Groq(api_key=os.environ.get("API_KEY")) │
│                                     │
│ chat_completion = client.chat.completions.create( │
│   model="llama-3.3-70b-versatile"  │
│   messages=[...]                   │
│ )                                  │
└─────────────────────────────────────┘

🔍 PROBLÈME IDENTIFIÉ DANS VOTRE RAG :
====================================

❌ Le chunking fragmente les informations importantes
❌ "55 litiges" est probablement coupé entre plusieurs chunks
❌ La recherche de similarité ne trouve pas le bon chunk

💡 SOLUTIONS :
- Réduire CHUNK_SIZE à 500-700
- Augmenter CHUNK_OVERLAP à 300
- Récupérer plus de chunks (k=10-15 au lieu de 5)
- Améliorer le prompt pour être plus précis

📊 FLUX DE DONNÉES :
==================

Documents → Chunks → Embeddings → MongoDB
    ↓
Question utilisateur → Embedding question
    ↓
Recherche similarité dans MongoDB
    ↓
Récupération des meilleurs chunks
    ↓
Envoi à Groq LLM avec prompt
    ↓
Réponse générée
"""
