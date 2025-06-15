import re
from typing import List, Dict
import nltk
from nltk.tokenize import sent_tokenize

# Télécharger les données NLTK nécessaires
def ensure_nltk_resources():
    """S'assurer que les ressources NLTK nécessaires sont disponibles."""
    resources = ['punkt', 'punkt_tab']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            try:
                print(f"📥 Téléchargement de la ressource NLTK: {resource}")
                nltk.download(resource, quiet=True)
            except Exception as e:
                print(f"⚠️  Erreur lors du téléchargement de {resource}: {e}")

# Initialiser les ressources NLTK
ensure_nltk_resources()

def is_important_boundary(text: str, pos: int) -> bool:
    """
    Détermine si une position est une bonne frontière pour couper
    """
    if pos <= 0 or pos >= len(text):
        return False
    
    # Éviter de couper au milieu de nombres ou dates
    if text[pos-1].isdigit() and text[pos].isdigit():
        return False
    
    # Éviter de couper au milieu de mots
    if text[pos-1].isalnum() and text[pos].isalnum():
        return False
    
    return True

def preserve_important_entities(text: str) -> List[tuple]:
    """
    Identifie les entités importantes qui ne doivent pas être coupées
    """
    entities = []
    
    # Nombres avec unités (€, %, jours, etc.)
    number_patterns = [
        r'\d+\s*€',
        r'\d+\s*%',
        r'\d+\s+jours?',
        r'\d+\s+euros?',
        r'\d{1,3}(?:\s\d{3})*\s*€',  # 2 050 €
    ]
    
    for pattern in number_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            entities.append((match.start(), match.end(), 'NUMBER'))
    
    # Dates
    date_patterns = [
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
        r'en \d{4}',
        r'2023[-\s]?2024',
    ]
    
    for pattern in date_patterns:
        for match in re.finditer(pattern, text):
            entities.append((match.start(), match.end(), 'DATE'))
    
    return entities

def smart_split_text_into_chunks(text: str, chunk_size: int = 1500, overlap: int = 300) -> List[str]:
    """
    Découpe intelligent d'un texte en chunks avec préservation des entités importantes
    """
    if len(text) <= chunk_size:
        return [text]
    
    # Identifier les entités importantes
    entities = preserve_important_entities(text)
    
    # Utiliser NLTK pour une meilleure segmentation par phrases
    try:
        sentences = sent_tokenize(text, language='french')
    except:
        # Fallback si NLTK ne fonctionne pas
        sentences = re.split(r'[.!?]+\s+', text)
    
    chunks = []
    current_chunk = ""
    current_size = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Si ajouter cette phrase dépasserait la taille limite
        if current_size + len(sentence) > chunk_size and current_chunk:
            # Vérifier qu'on ne coupe pas une entité importante
            safe_to_cut = True
            chunk_end = len(current_chunk)
            
            for start, end, entity_type in entities:
                if start < chunk_end < end:
                    safe_to_cut = False
                    break
            
            if safe_to_cut:
                chunks.append(current_chunk.strip())
                # Gérer le chevauchement intelligemment
                if len(current_chunk) > overlap:
                    overlap_text = current_chunk[-overlap:]
                    # Commencer le nouveau chunk par une phrase complète
                    overlap_sentences = sent_tokenize(overlap_text, language='french')
                    if len(overlap_sentences) > 1:
                        current_chunk = overlap_sentences[-1] + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    current_chunk = sentence
                current_size = len(current_chunk)
            else:
                # Forcer l'ajout de la phrase si on ne peut pas couper
                current_chunk += " " + sentence
                current_size += len(sentence) + 1
        else:
            # Ajouter la phrase au chunk actuel
            if current_chunk:
                current_chunk += " " + sentence
                current_size += len(sentence) + 1
            else:
                current_chunk = sentence
                current_size = len(sentence)
    
    # Ajouter le dernier chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Découpe un texte en chunks avec un chevauchement (VERSION AMÉLIORÉE)
    """
    # Utiliser la version smart par défaut
    return smart_split_text_into_chunks(text, chunk_size, overlap)

def split_document_into_chunks(document: Dict, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Découpe un document en chunks avec métadonnées enrichies
    """
    # Nettoyer le contenu avant chunking
    content = document['content']
    
    # ÉTAPE 1: Corriger l'alignement des tableaux (générique)
    content = fix_table_alignment(content)
    
    # ÉTAPE 2: Ajouter des métadonnées contextuelles
    content = add_contextual_metadata(content)
    
    # ÉTAPE 3: Préserver les structures importantes
    content = re.sub(r'\n{3,}', '\n\n', content)  # Réduire les sauts de ligne excessifs
    content = re.sub(r'\s{3,}', ' ', content)     # Réduire les espaces excessifs
    
    chunks = split_text_into_chunks(content, chunk_size, overlap)
    
    result = []
    for i, chunk_text in enumerate(chunks):
        # Analyser le contenu pour des métadonnées avancées
        has_numbers = bool(re.search(r'\d+', chunk_text))
        has_dates = bool(re.search(r'\d{4}', chunk_text))
        has_currency = bool(re.search(r'€|\d+\s*euros?', chunk_text, re.IGNORECASE))
        has_percentages = bool(re.search(r'\d+\s*%', chunk_text))
        
        # Détecter les associations label-valeur explicites
        has_explicit_values = bool(re.search(r':\s*\d+', chunk_text))
        
        # Identifier le type de contenu
        content_type = "general"
        if "[SECTION: DONNÉES CHIFFRÉES]" in chunk_text:
            content_type = "statistical"
        elif "[SECTION: PRÉVENTION DES LITIGES]" in chunk_text:
            content_type = "prevention"
        
        # Enrichir les métadonnées
        chunk_doc = {
            'source': document['source'],
            'content': chunk_text,
            'chunk_index': i,
            'total_chunks': len(chunks),
            'metadata': {
                'source': document['source'],
                'chunk_size': len(chunk_text),
                'has_numbers': has_numbers,
                'has_dates': has_dates,
                'has_currency': has_currency,
                'has_percentages': has_percentages,
                'has_explicit_values': has_explicit_values,
                'content_type': content_type,
                'quality_score': calculate_chunk_quality(chunk_text)
            }
        }
        result.append(chunk_doc)
    
    return result

def calculate_chunk_quality(text: str) -> float:
    """
    Calcule un score de qualité pour un chunk basé sur sa structure
    """
    score = 0.0
    
    # Points pour structure claire
    if ':' in text:
        score += 0.3  # Associations label-valeur explicites
    
    # Points pour contenu informatif
    if len(text.split()) > 20:
        score += 0.2  # Contenu substantiel
    
    # Points pour données structurées
    if re.search(r'\d+', text):
        score += 0.2  # Contient des données chiffrées
    
    # Points pour phrases complètes
    sentences = text.count('.') + text.count('!') + text.count('?')
    if sentences > 0:
        score += min(0.3, sentences * 0.1)
    
    # Pénalités pour problèmes
    if len(text) < 50:
        score -= 0.2  # Trop court
    
    if text.count('\n') > len(text) / 20:
        score -= 0.1  # Trop fragmenté
    
    return max(0.0, min(1.0, score))

def process_documents_chunks(documents: List[Dict], chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Traite une liste de documents et les découpe en chunks (VERSION AMÉLIORÉE)
    """
    all_chunks = []
    
    print(f"Découpage de {len(documents)} documents en chunks...")
    print(f"📏 Paramètres: chunk_size={chunk_size}, overlap={overlap}")
    
    for doc_idx, doc in enumerate(documents):
        print(f"  📄 Document {doc_idx + 1}/{len(documents)}: {doc.get('source', 'Unknown')}")
        doc_chunks = split_document_into_chunks(doc, chunk_size, overlap)
        all_chunks.extend(doc_chunks)
    
    # Statistiques sur les chunks
    chunk_sizes = [len(chunk['content']) for chunk in all_chunks]
    avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
    
    return all_chunks

def fix_table_alignment(text: str) -> str:
    """
    Améliore l'extraction PDF de manière générique et fiable
    Corrige les alignements de tableaux sans être spécifique à un document
    """
    lines = text.split('\n')
    improved_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Détecter les séquences: Label -> Nombre -> Unité/Label suivant
        if (i < len(lines) - 2 and 
            len(line) > 5 and 
            not re.match(r'^\d', line) and  # Ce n'est pas un nombre
            not line.endswith(':') and      # Ce n'est pas déjà formaté
            re.search(r'[a-zA-Z]', line)):  # Contient des lettres
            
            next_line = lines[i + 1].strip()
            third_line = lines[i + 2].strip() if i + 2 < len(lines) else ""
            
            # Pattern 1: Label -> Nombre simple -> Ligne suivante
            if (re.match(r'^\d+$', next_line) and 
                third_line and 
                not re.match(r'^\d+$', third_line)):
                
                # Si la troisième ligne semble être une unité ou un montant
                if re.match(r'^[\d\s,]+\s*€', third_line):
                    # Cas: Label -> Nombre -> Montant => Le montant va avec le label
                    improved_lines.append(f"{line}: {third_line}")
                    if i + 3 < len(lines):
                        fourth_line = lines[i + 3].strip()
                        if fourth_line and not re.match(r'^\d', fourth_line):
                            improved_lines.append(f"{fourth_line}: {next_line}")
                            i += 4
                            continue
                    i += 3
                    continue
                else:
                    # Cas normal: Label -> Nombre
                    improved_lines.append(f"{line}: {next_line}")
                    i += 2
                    continue
            
            # Pattern 2: Label -> Montant direct
            elif re.match(r'^[\d\s,]+\s*€', next_line):
                improved_lines.append(f"{line}: {next_line}")
                i += 2
                continue
        
        # Ignorer les lignes qui sont juste des nombres isolés (déjà traitées)
        if not re.match(r'^\d+$', line):
            improved_lines.append(line)
        
        i += 1
    
    # Post-traitement: nettoyer et structurer
    result = '\n'.join(improved_lines)
    
    # Nettoyer les espaces excessifs
    result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
    result = re.sub(r':\s+:', ':', result)
    
    return result

def add_contextual_metadata(text: str) -> str:
    """
    Ajoute des métadonnées contextuelles pour aider le LLM à mieux comprendre
    """
    # Identifier et marquer les sections importantes
    enhanced_text = text
    
    # Marquer les sections de chiffres
    if re.search(r'(chiffres?\s+principaux|statistiques?|données?\s+numériques?)', text, re.IGNORECASE):
        enhanced_text = "[SECTION: DONNÉES CHIFFRÉES]\n" + enhanced_text
    
    # Marquer les sections de prévention
    if re.search(r'(prévention|anticipation|éviter|situations?\s+litigieuses?)', text, re.IGNORECASE):
        enhanced_text = "[SECTION: PRÉVENTION DES LITIGES]\n" + enhanced_text
    
    # Ajouter des clarifications pour les nombres ambigus
    lines = enhanced_text.split('\n')
    clarified_lines = []
    
    for line in lines:
        # Si une ligne contient à la fois un petit nombre ET un grand nombre
        numbers = re.findall(r'\b\d{1,3}(?:\s\d{3})*\b', line)
        if len(numbers) >= 2:
            # Ajouter une note explicative
            clarified_lines.append(line)
            clarified_lines.append("[NOTE: Cette ligne contient plusieurs valeurs numériques]")
        else:
            clarified_lines.append(line)
    
    return '\n'.join(clarified_lines)
