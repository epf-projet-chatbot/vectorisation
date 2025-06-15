#!/usr/bin/env python3
"""
Script d'initialisation pour télécharger les ressources NLTK nécessaires.
À exécuter après l'installation des requirements.
"""

import nltk
import ssl

def download_nltk_resources():
    """Télécharge les ressources NLTK nécessaires pour le chunker avancé."""
    
    try:
        # Pour éviter les problèmes SSL sur certains systèmes
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        
        print("📥 Téléchargement des ressources NLTK...")
        
        # Ressources nécessaires pour le chunker avancé
        resources = [
            'punkt',      # Pour la segmentation des phrases
            'punkt_tab',  # Nouvelle version de punkt
            'stopwords',  # Mots vides (optionnel mais utile)
            'averaged_perceptron_tagger',  # POS tagging (optionnel)
        ]
        
        for resource in resources:
            try:
                print(f"  ⬇️  Téléchargement de '{resource}'...")
                nltk.download(resource, quiet=True)
                print(f"  ✅ '{resource}' téléchargé avec succès")
            except Exception as e:
                print(f"  ⚠️  Erreur lors du téléchargement de '{resource}': {e}")
        
        print("\n🎉 Configuration NLTK terminée !")
        
        # Test rapide pour vérifier que tout fonctionne
        print("\n🧪 Test rapide...")
        try:
            from nltk.tokenize import sent_tokenize
            test_text = "Ceci est une phrase de test. Voici une seconde phrase."
            sentences = sent_tokenize(test_text, language='french')
            print(f"  ✅ Segmentation testée: {len(sentences)} phrases détectées")
        except Exception as e:
            print(f"  ❌ Erreur de test: {e}")
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    download_nltk_resources()
