"""
Module de pré-traitement des données textuelles
"""

import re
import unicodedata
from typing import List, Set, Optional
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

# Télécharger les ressources NLTK nécessaires
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextPreprocessor:
    """Classe pour le pré-traitement des textes"""
    
    def __init__(self, language: str = 'french'):
        """
        Initialise le préprocesseur
        
        Args:
            language: Langue pour les stop words et le stemming ('french', 'english')
        """
        self.language = language
        
        # Stop words
        try:
            self.stop_words = set(stopwords.words(language))
        except OSError:
            print(f"Stop words pour {language} non disponibles, utilisation des stop words anglais")
            self.stop_words = set(stopwords.words('english'))
        
        # Ajouter des stop words personnalisés pour le domaine juridique
        custom_stop_words = {
            'article', '\n', 'alinéa', 'paragraphe', 'section', 'chapitre', 'titre',
            'code', 'loi', 'décret', 'arrêté', 'ordonnance', 'règlement',
            'cf', 'voir', 'notamment', 'ainsi', 'donc', 'cependant', 'toutefois',
            'néanmoins', 'par', 'pour', 'avec', 'sans', 'sous', 'sur', 'dans'
        }
        
        self.stop_words.update(custom_stop_words)
        
        # Stemmer
        try:
            self.stemmer = SnowballStemmer(language)
        except ValueError:
            print(f"Stemmer pour {language} non disponible, utilisation du stemmer anglais")
            self.stemmer = SnowballStemmer('english')
        
        # Motifs de nettoyage
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+33|0)[1-9](?:[0-9]{8})')
        self.number_pattern = re.compile(r'\b\d+(?:\.\d+)?\b')
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        self.multiple_spaces_pattern = re.compile(r'\s+')
        
        # Motifs pour le texte juridique
        self.legal_references_pattern = re.compile(r'(art\.|article)\s*\d+(?:-\d+)?', re.IGNORECASE)
        self.date_pattern = re.compile(r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b')
    
    def remove_accents(self, text: str) -> str:
        """
        Supprime les accents d'un texte
        
        Args:
            text: Texte à traiter
            
        Returns:
            Texte sans accents
        """
        # Normalisation NFD (décomposition canonique)
        nfd = unicodedata.normalize('NFD', text)
        # Suppression des caractères de combinaison (accents)
        without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        return without_accents
    
    def clean_text(self, text: str) -> str:
        """
        Nettoie le texte en supprimant URLs, emails, numéros de téléphone, etc.
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        if not text:
            return ""
        
        # Conversion en minuscules
        text = text.lower()
        
        # Suppression des URLs
        text = self.url_pattern.sub(' ', text)
        
        # Suppression des emails
        text = self.email_pattern.sub(' ', text)
        
        # Suppression des numéros de téléphone
        text = self.phone_pattern.sub(' ', text)
        
        # Suppression des caractères de ponctuation
        text = self.punctuation_pattern.sub(' ', text)
        
        # Suppression des espaces multiples
        text = self.multiple_spaces_pattern.sub(' ', text)
        
        return text.strip()
    
    def remove_stop_words(self, tokens: List[str]) -> List[str]:
        """
        Supprime les stop words d'une liste de tokens
        
        Args:
            tokens: Liste de tokens
            
        Returns:
            Liste de tokens sans stop words
        """
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Applique le stemming à une liste de tokens
        
        Args:
            tokens: Liste de tokens
            
        Returns:
            Liste de tokens après stemming
        """
        return [self.stemmer.stem(token) for token in tokens]
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenise un texte
        
        Args:
            text: Texte à tokeniser
            
        Returns:
            Liste de tokens
        """
        try:
            tokens = word_tokenize(text, language=self.language)
        except LookupError:
            # Fallback vers une tokenisation simple
            tokens = text.split()
        
        # Filtrer les tokens trop courts ou qui ne contiennent que des espaces
        tokens = [token for token in tokens if len(token) > 2 and token.strip()]
        
        return tokens
    
    def preprocess_text(self, 
                       text: str, 
                       remove_accents: bool = True,
                       remove_stop_words: bool = True,
                       apply_stemming: bool = False,
                       min_token_length: int = 2) -> str:
        """
        Pipeline complète de pré-traitement d'un texte
        
        Args:
            text: Texte à traiter
            remove_accents: Supprimer les accents
            remove_stop_words: Supprimer les stop words
            apply_stemming: Appliquer le stemming
            min_token_length: Longueur minimale des tokens
            
        Returns:
            Texte préprocessé
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Nettoyage initial
        processed_text = self.clean_text(text)
        
        # Suppression des accents
        if remove_accents:
            processed_text = self.remove_accents(processed_text)
        
        # Tokenisation
        tokens = self.tokenize(processed_text)
        
        # Filtrage par longueur minimale
        tokens = [token for token in tokens if len(token) >= min_token_length]
        
        # Suppression des stop words
        if remove_stop_words:
            tokens = self.remove_stop_words(tokens)
        
        # Stemming
        if apply_stemming:
            tokens = self.stem_tokens(tokens)
        
        return ' '.join(tokens)
    
    def preprocess_document_chunks(self, 
                                  chunks: List[str], 
                                  **kwargs) -> List[str]:
        """
        Préprocesse une liste de chunks de documents
        
        Args:
            chunks: Liste des chunks à traiter
            **kwargs: Arguments pour preprocess_text
            
        Returns:
            Liste des chunks préprocessés
        """
        processed_chunks = []
        
        for chunk in chunks:
            processed_chunk = self.preprocess_text(chunk, **kwargs)
            if processed_chunk:  # Ne garder que les chunks non vides après traitement
                processed_chunks.append(processed_chunk)
        
        return processed_chunks
    
    def add_custom_stop_words(self, words: Set[str]) -> None:
        """
        Ajoute des stop words personnalisés
        
        Args:
            words: Ensemble de mots à ajouter aux stop words
        """
        self.stop_words.update(words)
    
    def remove_custom_stop_words(self, words: Set[str]) -> None:
        """
        Supprime des stop words personnalisés
        
        Args:
            words: Ensemble de mots à supprimer des stop words
        """
        self.stop_words.difference_update(words)


# Instance par défaut
default_preprocessor = TextPreprocessor()

def preprocess_text(text: str, 
                   remove_accents: bool = True,
                   remove_stop_words: bool = True,
                   apply_stemming: bool = False,
                   min_token_length: int = 2) -> str:
    """
    Fonction wrapper pour préprocesser un texte avec l'instance par défaut
    
    Args:
        text: Texte à traiter
        remove_accents: Supprimer les accents
        remove_stop_words: Supprimer les stop words
        apply_stemming: Appliquer le stemming
        min_token_length: Longueur minimale des tokens
        
    Returns:
        Texte préprocessé
    """
    return default_preprocessor.preprocess_text(
        text=text,
        remove_accents=remove_accents,
        remove_stop_words=remove_stop_words,
        apply_stemming=apply_stemming,
        min_token_length=min_token_length
    )
