""" Calcul du PCC pour évaluer la performance du RAG sur une BDD de test """
import os
from groq import Groq
from rag import k_context_vectors, make_vector
from mongo import init_connection

samples = [
    ("Peut-on avoir un JEH à 70€ ?", "non"),
    ("Peut-on être appelés consultants ?", "non"),
    ("L'intervenant peut-il communiquer directement avec le client ?", "non"),
    ("Quelle est la durée de la garantie pour un PDF ?", "2 semaines"),
    ("Quelle est la durée de la garantie pour un document qui n'est pas un PDF ?", "3 mois"),
    ("Peut-on avoir une cotisation sous forme de droit d'entrée ?", "oui"),
    ("Peut-on utiliser une seul JEH pour payer 2 intervenants ?", "non"),
    ("Puis-je faire un avenant par mail ?", "oui"),
    ("L'intervenant doit-il être étudiant jusqu'à la fin de l'étude ?", "oui"),
    ("Combien faut-il de personnes pour créer une association de la loi 1901 au minimum ?", "2"),
    ("A-t-on droit aux apporteurs d'affaires ?", "non"),
    ("Peut-on présenter directement au client une CE ?", "oui"),
    ("Quel est le smic actuel ?", "11,88 €"),
    ("Est-il possible de continuer un bon de commande après la fin de validité de la convention cadre ?", "non"),
    ("Peut-on faire un avenant au bon de commande ?", "non"),
]

def rag_generate_response(question):
    """
    Génération d'une réponse par le RAG.
    
    Args:
        question: La question à laquelle le RAG doit répondre.
        
    Returns:
        Une réponse basée sur la question.
    """
    init_connection()
    
    # Récupérer le contexte pertinent
    context = k_context_vectors(make_vector(question), k=5)
    
    # Construire le prompt avec le contexte
    context_text = "\n".join(context) if context else "Aucun contexte trouvé."
    prompt = f"Contexte: {context_text}\n\nQuestion: {question}\n\nRéponse:"
    
    client = Groq(api_key=os.environ.get("API_KEY"),)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Tu es un assistant juridique. Réponds précisément aux questions en te basant sur le contexte fourni."
            },
            {
                "role": "user", 
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    reponse = chat_completion.choices[0].message.content
    return reponse

def calculate_pcc(samples):
    """
    Calcule le pourcentage de réponses correctes (PCC) pour un ensemble d'échantillons.
    
    Args:
        samples: Liste de tuples (question, réponse attendue).
        
    Returns:
        Le pourcentage de réponses correctes.
    """
    correct_count = 0
    
    for question, expected_answer in samples:
        # Simuler la génération de la réponse par le RAG
        response = rag_generate_response(question)
        
        if response in expected_answer:
            correct_count += 1
    
    pcc = (correct_count / len(samples)) * 100
    return pcc

def test_individual_question(question):
    """
    Teste une question individuelle et affiche le processus détaillé.
    
    Args:
        question: La question à tester.
    """
    print(f"\n{'='*60}")
    print(f"QUESTION: {question}")
    print(f"{'='*60}")
    
    try:
        # Étape 1: Vectorisation de la question
        print("\n1. Vectorisation de la question...")
        vector = make_vector(question)
        print(f"   ✓ Vecteur généré (dimension: {len(vector)})")
        
        # Étape 2: Recherche de contexte
        print("\n2. Recherche de contexte pertinent...")
        context = k_context_vectors(vector, k=5)
        print(f"   ✓ {len(context)} chunks de contexte trouvés")
        
        # Afficher le contexte trouvé
        print("\n3. Contexte récupéré:")
        for i, chunk in enumerate(context, 1):
            preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
            print(f"   Chunk {i}: {preview}")
        
        # Étape 3: Génération de la réponse
        print("\n4. Génération de la réponse...")
        response = rag_generate_response(question)
        print(f"\n✅ RÉPONSE: {response}")
        
        return response
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return None

def test_database_connection():
    """
    Teste la connexion à la base de données MongoDB.
    """
    print("\n📊 Test de connexion à la base de données...")
    try:
        from mongo import test_connection, count_documents, get_collection_stats
        
        if test_connection():
            print("   ✅ Connexion MongoDB réussie")
            doc_count = count_documents()
            print(f"   📄 Nombre de documents: {doc_count}")
            
            stats = get_collection_stats()
            print(f"   📈 Statistiques: {stats}")
            return True
        else:
            print("   ❌ Échec de connexion MongoDB")
            return False
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        return False

def run_performance_test():
    """
    Lance le test de performance complet sur tous les échantillons.
    """
    print("\n🧪 LANCEMENT DU TEST DE PERFORMANCE COMPLET")
    print("="*60)
    
    correct_count = 0
    total_questions = len(samples)
    
    for i, (question, expected_answer) in enumerate(samples, 1):
        print(f"\n[{i}/{total_questions}] Test: {question[:50]}...")
        
        try:
            response = rag_generate_response(question)
            
            # Vérification simplifiée de la réponse
            is_correct = expected_answer.lower() in response.lower()
            
            if is_correct:
                correct_count += 1
                print(f"   ✅ CORRECT (attendu: {expected_answer})")
            else:
                print(f"   ❌ INCORRECT (attendu: {expected_answer}, obtenu: {response[:50]}...)")
                
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")
    
    pcc = (correct_count / total_questions) * 100
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS FINAUX:")
    print(f"   • Questions correctes: {correct_count}/{total_questions}")
    print(f"   • Pourcentage de réussite (PCC): {pcc:.1f}%")
    print(f"{'='*60}")
    
    return pcc

def interactive_mode():
    """
    Mode interactif permettant de poser des questions en temps réel.
    """
    print("\n💬 MODE INTERACTIF")
    print("="*40)
    print("Tapez vos questions (tapez 'quit' pour quitter)")
    
    while True:
        try:
            question = input("\n❓ Votre question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir!")
                break
                
            if not question:
                continue
                
            response = test_individual_question(question)
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

def show_menu():
    """
    Affiche le menu principal de l'interface.
    """
    print("\n" + "="*60)
    print("🤖 INTERFACE DE TEST RAG - CHATBOT JURIDIQUE")
    print("="*60)
    print("1. Tester la connexion à la base de données")
    print("2. Tester une question spécifique")
    print("3. Lancer le test de performance complet")
    print("4. Mode interactif (questions libres)")
    print("5. Afficher les échantillons de test")
    print("6. Quitter")
    print("="*60)

def show_samples():
    """
    Affiche tous les échantillons de test disponibles.
    """
    print("\n📋 ÉCHANTILLONS DE TEST DISPONIBLES:")
    print("="*50)
    
    for i, (question, answer) in enumerate(samples, 1):
        print(f"{i:2d}. Q: {question}")
        print(f"     R: {answer}")
        print("-" * 50)

def main():
    """
    Fonction principale de l'interface.
    """
    while True:
        try:
            show_menu()
            choice = input("\n🔥 Votre choix (1-6): ").strip()
            
            if choice == '1':
                test_database_connection()
                
            elif choice == '2':
                print("\n📝 Test d'une question spécifique")
                question = input("❓ Entrez votre question: ").strip()
                if question:
                    test_individual_question(question)
                    
            elif choice == '3':
                run_performance_test()
                
            elif choice == '4':
                interactive_mode()
                
            elif choice == '5':
                show_samples()
                
            elif choice == '6':
                print("\n👋 Au revoir!")
                break
                
            else:
                print("\n❌ Choix invalide. Veuillez entrer un nombre entre 1 et 6.")
                
            input("\n⏸️  Appuyez sur Entrée pour continuer...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            input("\n⏸️  Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()