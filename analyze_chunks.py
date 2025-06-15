#!/usr/bin/env python3
"""
Script pour analyser la qualité du chunking et valider les améliorations
"""

import os
import sys
from mongo import init_connection, collection
from config import config
from chunker import preserve_important_entities, smart_split_text_into_chunks

def analyze_chunk_quality():
    """Analyse la qualité des chunks créés"""
    
    # S'assurer de la connexion
    init_connection()
    
    if collection is None:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    # Informations générales
    total_docs = collection.count_documents({})
    database_name = config.get_database_name()
    mode = "TEST" if config.test_mode else "PRODUCTION"
    
    print(f"🔍 ANALYSE DE LA QUALITÉ DU CHUNKING")
    print(f"=" * 50)
    print(f"🎯 Mode: {mode}")
    print(f"📁 Base: {database_name}")
    print(f"📈 Total chunks: {total_docs}")
    print()
    
    if total_docs == 0:
        print("⚠️  Aucun document trouvé dans la base de données")
        return
    
    # Récupérer des échantillons pour analyser
    sample_docs = list(collection.find({}).limit(20))
    
    print("🧮 ANALYSE DES ENTITÉS IMPORTANTES:")
    print("-" * 40)
    
    entities_stats = {
        'chunks_with_numbers': 0,
        'chunks_with_dates': 0,
        'chunks_with_currency': 0,
        'chunks_with_key_info': 0,
        'total_chunks': len(sample_docs)
    }
    
    key_patterns = [
        r'\d+\s+litiges?\s+déclarés?',  # "55 litiges déclarés"
        r'nombre\s+de\s+litiges',       # "nombre de litiges"
        r'durée\s+moyenne',             # "durée moyenne"
        r'préjudice\s+médian',          # "préjudice médian"
        r'\d+\s+jours',                 # "173 jours"
        r'\d+\s*€',                     # "2050 €"
    ]
    
    print("🔍 Recherche d'informations clés dans les chunks:")
    
    chunks_with_key_info = []
    
    for i, doc in enumerate(sample_docs):
        content = doc.get('content', '')
        
        # Analyser les métadonnées
        if doc.get('metadata', {}).get('has_numbers'):
            entities_stats['chunks_with_numbers'] += 1
        if doc.get('metadata', {}).get('has_dates'):
            entities_stats['chunks_with_dates'] += 1
        if doc.get('metadata', {}).get('has_currency'):
            entities_stats['chunks_with_currency'] += 1
        
        # Chercher des patterns spécifiques importants
        found_patterns = []
        for pattern in key_patterns:
            import re
            if re.search(pattern, content, re.IGNORECASE):
                found_patterns.append(pattern)
        
        if found_patterns:
            entities_stats['chunks_with_key_info'] += 1
            chunks_with_key_info.append({
                'chunk_index': i,
                'source': doc.get('source', 'Unknown'),
                'patterns': found_patterns,
                'content_preview': content[:150] + '...' if len(content) > 150 else content
            })
    
    # Afficher les statistiques
    print(f"📊 Chunks avec nombres: {entities_stats['chunks_with_numbers']}/{entities_stats['total_chunks']}")
    print(f"📊 Chunks avec dates: {entities_stats['chunks_with_dates']}/{entities_stats['total_chunks']}")
    print(f"📊 Chunks avec devises: {entities_stats['chunks_with_currency']}/{entities_stats['total_chunks']}")
    print(f"📊 Chunks avec infos clés: {entities_stats['chunks_with_key_info']}/{entities_stats['total_chunks']}")
    
    print(f"\n🎯 CHUNKS CONTENANT DES INFORMATIONS CLÉS:")
    print("-" * 50)
    
    for chunk_info in chunks_with_key_info[:5]:  # Afficher les 5 premiers
        print(f"📄 Chunk {chunk_info['chunk_index']} - {chunk_info['source']}")
        print(f"🔍 Patterns trouvés: {', '.join(chunk_info['patterns'])}")
        print(f"📝 Aperçu: {chunk_info['content_preview']}")
        print()
    
    # Test de recherche spécifique
    print(f"🔍 RECHERCHE SPÉCIFIQUE: 'nombre de litiges déclarés'")
    print("-" * 50)
    
    import re
    matching_chunks = []
    for doc in sample_docs:
        content = doc.get('content', '')
        if re.search(r'55|litiges?\s+déclarés?|nombre.*litiges', content, re.IGNORECASE):
            matching_chunks.append({
                'source': doc.get('source', 'Unknown'),
                'chunk_index': doc.get('chunk_index', 'Unknown'),
                'content': content
            })
    
    print(f"📈 Chunks correspondants trouvés: {len(matching_chunks)}")
    
    for chunk in matching_chunks[:3]:  # Afficher les 3 premiers
        print(f"📄 Source: {chunk['source']} (chunk {chunk['chunk_index']})")
        print(f"📝 Contenu: {chunk['content'][:200]}...")
        print()
    
    return entities_stats

def test_chunking_algorithm():
    """Teste l'algorithme de chunking sur un texte exemple"""
    
    print(f"🧪 TEST DE L'ALGORITHME DE CHUNKING")
    print(f"=" * 50)
    
    # Texte de test avec des entités importantes
    test_text = """
    Analyse des litiges - Les chiffres principaux en 2023
    
    Le nombre de litiges déclarés en 2023 est de 55. Cette augmentation par rapport 
    à l'année précédente représente une progression de 15%. Le préjudice médian 
    s'élève à 2 050 € par litige.
    
    La durée moyenne de résolution est de 173 jours, ce qui constitue une amélioration 
    par rapport aux 185 jours de 2022. M. Dupont, directeur juridique, a validé ces chiffres.
    
    Note importante: Tous les montants présentés sont en H.T. Un litige est un désaccord 
    entre une Junior-Entreprise et un client ou un intervenant.
    """
    
    print("📝 TEXTE DE TEST:")
    print(test_text)
    print()
    
    # Tester l'identification des entités
    entities = preserve_important_entities(test_text)
    print(f"🔍 ENTITÉS IMPORTANTES DÉTECTÉES:")
    for start, end, entity_type in entities:
        entity_text = test_text[start:end]
        print(f"  {entity_type}: '{entity_text}' (position {start}-{end})")
    print()
    
    # Tester le chunking
    chunks = smart_split_text_into_chunks(test_text, chunk_size=200, overlap=50)
    
    print(f"✂️ RÉSULTAT DU CHUNKING (taille max: 200, overlap: 50):")
    print(f"📊 Nombre de chunks créés: {len(chunks)}")
    print()
    
    for i, chunk in enumerate(chunks):
        print(f"--- CHUNK {i+1} ({len(chunk)} caractères) ---")
        print(chunk)
        print()

if __name__ == "__main__":
    # Vérifier les arguments de ligne de commande
    if "--test" in sys.argv:
        os.environ["TEST_MODE"] = "true"
        print("🧪 Mode TEST activé")
    elif "--prod" in sys.argv:
        os.environ["TEST_MODE"] = "false"
        print("🏭 Mode PRODUCTION activé")
    
    if "--algorithm-test" in sys.argv:
        test_chunking_algorithm()
    else:
        analyze_chunk_quality()
