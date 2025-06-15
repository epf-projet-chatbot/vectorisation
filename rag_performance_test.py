""" Calcul du PCC pour évaluer la performance du RAG sur une BDD de test """
import os
import sys
from groq import Groq
from rag import k_context_vectors, make_vector, k_context_vectors_smart
from mongo import init_connection

# Vérifier l'argument --test au démarrage
if "--test" in sys.argv:
    os.environ["TEST_MODE"] = "true"
    print("🧪 Mode TEST activé via argument --test")
elif "--prod" in sys.argv or "--production" in sys.argv:
    os.environ["TEST_MODE"] = "false"
    print("🏭 Mode PRODUCTION activé via argument --prod/--production")

samples = [
    ("Peut-on avoir un JEH à 70€ ?", "non"),
    ("Puis-je faire un avenant par mail ?", "oui"),
    ("Quel est le smic actuel ?", "11,88 €"),
    ("Peut-on être appelés consultants ?", "non"),
    ("Est-il possible de continuer un bon de commande après la fin de validité de la convention cadre ?", "non"),
    ("L'intervenant peut-il communiquer directement avec le client ?", "non"),
    ("A-t-on droit aux apporteurs d'affaires ?", "non"),
    ("Quelle est la durée de la garantie pour un PDF ?", "2 semaines"),
    ("Peut-on présenter directement au client une CE ?", "oui"),
    ("Quelle est la durée de la garantie pour un document qui n'est pas un PDF ?", "3 mois"),
    ("Peut-on avoir une cotisation sous forme de droit d'entrée ?", "oui"),
    ("Peut-on utiliser une seul JEH pour payer 2 intervenants ?", "non"),
    ("L'intervenant doit-il être étudiant jusqu'à la fin de l'étude ?", "oui"),
    ("Combien faut-il de personnes pour créer une association de la loi 1901 au minimum ?", "2"),
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
    test_database_connection()
    
    # Récupérer le contexte pertinent
    context = k_context_vectors(make_vector(question), k=8)
    
    # Construire le prompt avec le contexte
    context_text = "\n".join(context) if context else "Aucun contexte trouvé."
    prompt = f"Tu es un assistant juridique spécialisé dans les Junior-Entreprises (JE) françaises. Tu dois répondre aux questions des utilisateurs en t’appuyant exclusivement sur les documents fournis via le système de retrieval (lois, statuts, guides CNJE, jurisprudences, etc.). Lorsque tu réponds : Ne fournis des informations que si elles sont présentes dans les documents récupérés. Si une information ne figure pas dans les documents, indique clairement que tu ne peux pas répondre avec certitude, et invite l’utilisateur à consulter un expert juridique ou la CNJE. Sois concis, rigoureux et neutre dans le ton. Si une réponse comporte plusieurs cas possibles (ex. : selon le statut associatif ou non), énumère-les clairement. Contexte: {context_text}\n\nQuestion: {question}\n\nRéponse:"
    
    client = Groq(api_key=os.environ.get("API_KEY"),)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": ""            },
            {
                "role": "user", 
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",  # Modèles disponibles:
        # - "llama-3.3-70b-versatile"     (ACTUEL - Recommandé)
        # - "llama-3.1-70b-versatile"     (Plus ancien mais stable)
        # - "llama-3.1-8b-instant"        (Plus rapide, moins précis)
        # - "mixtral-8x7b-32768"          (Alternative Mixtral)
        # - "gemma2-9b-it"                (Modèle Google Gemma)
    )
    reponse = chat_completion.choices[0].message.content
    return reponse

def rag_generate_response_smart(question):
    """
    Version améliorée avec utilisation des métadonnées et prompt optimisé
    """
    init_connection()
    test_database_connection()
    
    # Détecter le type de question AVANT de l'utiliser
    is_quantitative = any(word in question.lower() for word in [
        "combien", "nombre", "quel est le", "quelle est la", "montant", "prix", "coût", 
        "durée", "pourcentage", "%", "€", "euros", "jours", "mois", "années"
    ])
    
    # Utiliser la version smart avec adaptation selon le type de question
    if is_quantitative:
        # Pour les questions chiffrées, privilégier les métadonnées
        context = k_context_vectors_smart(make_vector(question), k=6, prioritize_metadata=True)
    else:
        # Pour les questions qualitatives, plus de contexte et moins de restrictions
        context = k_context_vectors(make_vector(question), k=8)
    
    # Prompt adaptatif selon le type de question
    context_text = "\n\n---CHUNK---\n\n".join(context) if context else "Aucun contexte trouvé."
    
    if is_quantitative:
        # Prompt strict pour les questions quantitatives avec gestion d'ambiguïté
        prompt = f"""Tu es un assistant juridique expert en Junior-Entreprises françaises.

MISSION: Répondre avec une précision maximale aux questions CHIFFRÉES.

RÈGLES STRICTES:
1. Cherche les associations explicites avec ":" 
2. Si tu vois plusieurs chiffres dans le contexte, analyse leur CONTEXTE pour déterminer lequel correspond à la question
3. Pour "nombre de litiges" cherche un petit nombre (< 100), pour "préjudice/montant" cherche un nombre avec € ou plus grand
4. Si l'info chiffrée est ambiguë ou contradictoire, explique l'ambiguïté au lieu de deviner
5. Cite EXACTEMENT les chiffres trouvés avec leur contexte

ANALYSE DU CONTEXTE:
{context_text}

QUESTION: {question}

RÉPONSE CHIFFRÉE PRÉCISE:"""
    else:
        # Prompt flexible pour les questions qualitatives
        prompt = f"""Tu es un assistant juridique expert en Junior-Entreprises françaises.

MISSION: Répondre de manière complète et utile aux questions sur les Junior-Entreprises.

INSTRUCTIONS:
1. Utilise les informations du contexte fourni
2. Si le contexte est incomplet, utilise tes connaissances générales sur les Junior-Entreprises
3. Donne des conseils pratiques et utiles
4. Sois précis quand tu as des informations exactes
5. Reste dans le domaine des Junior-Entreprises françaises

CONTEXTE DISPONIBLE:
{context_text}

QUESTION: {question}

RÉPONSE COMPLÈTE ET UTILE:"""

    client = Groq(api_key=os.environ.get("API_KEY"),)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Tu es un assistant qui répond avec une précision factuelle absolue."
            },
            {
                "role": "user", 
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.1,  # Réduire la créativité pour plus de précision
    )
    return chat_completion.choices[0].message.content

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
        print(f"\n✅ RÉPONSE (Version classique): {response}")
        
        # Test également la version améliorée
        print("\n5. Test de la version améliorée...")
        response_smart = rag_generate_response_smart(question)
        print(f"\n🚀 RÉPONSE (Version améliorée): {response_smart}")
        
        return response_smart  # Retourner la version améliorée
        
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
    Lance le test de performance complet avec évaluation manuelle des réponses.
    """
    print("\n🧪 LANCEMENT DU TEST DE PERFORMANCE COMPLET")
    print("="*60)
    print("💡 Vous allez évaluer manuellement chaque réponse du système RAG")
    print("   Tapez 'o' ou 'oui' si la réponse est correcte")
    print("   Tapez 'n' ou 'non' si la réponse est incorrecte")
    print("   Tapez 's' pour passer une question")
    print("="*60)
    
    correct_count = 0
    total_questions = len(samples)
    skipped_questions = 0
    
    for i, (question, expected_answer) in enumerate(samples, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{total_questions}] QUESTION: {question}")
        print(f"RÉPONSE ATTENDUE: {expected_answer}")
        print(f"{'='*60}")
        
        try:
            # Générer la réponse du RAG
            print("\n🤖 Génération de la réponse par le RAG...")
            response = rag_generate_response(question)
            
            print(f"\n📝 RÉPONSE DU RAG:")
            print("-" * 40)
            print(f"{response}")
            print("-" * 40)
            
            # Demander l'évaluation à l'utilisateur
            while True:
                user_evaluation = input(f"\n❓ Cette réponse est-elle correcte? (o/oui/n/non/s/skip): ").strip().lower()
                
                if user_evaluation in ['o', 'oui', 'y', 'yes']:
                    correct_count += 1
                    print("   ✅ Marqué comme CORRECT")
                    break
                elif user_evaluation in ['n', 'non', 'no']:
                    print("   ❌ Marqué comme INCORRECT")
                    break
                elif user_evaluation in ['s', 'skip', 'passer']:
                    skipped_questions += 1
                    print("   ⏭️  Question passée")
                    break
                else:
                    print("   ⚠️  Réponse invalide. Utilisez 'o/oui', 'n/non', ou 's/skip'")
                
        except Exception as e:
            print(f"   ❌ ERREUR lors de la génération: {e}")
            skip = input("   Voulez-vous passer cette question? (o/n): ").strip().lower()
            if skip in ['o', 'oui', 'y', 'yes']:
                skipped_questions += 1
    
    # Calcul des résultats
    evaluated_questions = total_questions - skipped_questions
    pcc = (correct_count / evaluated_questions * 100) if evaluated_questions > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS FINAUX:")
    print(f"   • Questions totales: {total_questions}")
    print(f"   • Questions évaluées: {evaluated_questions}")
    print(f"   • Questions passées: {skipped_questions}")
    print(f"   • Réponses correctes: {correct_count}")
    print(f"   • Pourcentage de réussite (PCC): {pcc:.1f}%")
    print(f"{'='*60}")
    
    return pcc

def run_automatic_performance_test():
    """
    Lance le test de performance automatique (sans évaluation manuelle).
    """
    print("\n⚡ LANCEMENT DU TEST DE PERFORMANCE AUTOMATIQUE")
    print("="*60)
    
    correct_count = 0
    total_questions = len(samples)
    
    for i, (question, expected_answer) in enumerate(samples, 1):
        print(f"\n[{i}/{total_questions}] Test: {question[:50]}...")
        
        try:
            response = rag_generate_response(question)
            
            # Vérification automatique simplifiée
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
    print(f"📊 RÉSULTATS FINAUX (AUTOMATIQUE):")
    print(f"   • Questions correctes: {correct_count}/{total_questions}")
    print(f"   • Pourcentage de réussite (PCC): {pcc:.1f}%")
    print(f"   ⚠️  Note: Ce test utilise une vérification automatique simple")
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
    from config import config
    mode_info = "🧪 TEST" if config.test_mode else "🏭 PRODUCTION"
    db_name = config.get_database_name()
    
    # Vérifier si le mode a été défini par argument
    mode_source = ""
    if "--test" in sys.argv:
        mode_source = " (via --test)"
    elif "--prod" in sys.argv or "--production" in sys.argv:
        mode_source = " (via --prod)"
    
    print("\n" + "="*60)
    print("🤖 INTERFACE DE TEST RAG - CHATBOT JURIDIQUE")
    print(f"📊 Mode actuel: {mode_info}{mode_source} (Base: {db_name})")
    print("="*60)
    print("1. Tester la connexion à la base de données")
    print("2. Tester une question spécifique")
    print("3. Test de performance avec évaluation manuelle")
    print("4. Test de performance automatique (rapide)")
    print("5. Mode interactif (questions libres)")
    print("6. Afficher les échantillons de test")
    print("7. Basculer entre mode TEST/PRODUCTION")
    print("8. Quitter")
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

def toggle_test_mode():
    """
    Bascule entre le mode test et le mode production
    """
    from config import config
    import os
    
    current_mode = "TEST" if config.test_mode else "PRODUCTION"
    new_mode = "PRODUCTION" if config.test_mode else "TEST"
    
    print(f"\n🔄 BASCULEMENT DE MODE")
    print("=" * 40)
    print(f"Mode actuel: {current_mode}")
    print(f"Nouveau mode: {new_mode}")
    
    if config.test_mode:
        print(f"📊 Base actuelle: {config.get_database_name()}")
        print(f"📊 Nouvelle base: {config.database_name}")
    else:
        print(f"📊 Base actuelle: {config.get_database_name()}")
        print(f"📊 Nouvelle base: {config.test_database_name}")
    
    confirm = input(f"\n❓ Voulez-vous passer en mode {new_mode}? (o/n): ").strip().lower()
    
    if confirm in ['o', 'oui', 'y', 'yes']:
        # Modifier la variable d'environnement
        new_test_mode = "false" if config.test_mode else "true"
        
        # Lire le fichier .env
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Modifier la ligne TEST_MODE
            for i, line in enumerate(lines):
                if line.startswith('TEST_MODE='):
                    lines[i] = f'TEST_MODE={new_test_mode}\n'
                    break
            else:
                # Ajouter la ligne si elle n'existe pas
                lines.append(f'TEST_MODE={new_test_mode}\n')
            
            # Écrire le fichier modifié
            with open(env_path, 'w') as f:
                f.writelines(lines)
            
            print(f"✅ Mode {new_mode} activé!")
            print("⚠️  Redémarrez le programme pour que les changements prennent effet")
        else:
            print("❌ Fichier .env non trouvé")
    else:
        print("❌ Changement annulé")

def main():
    """
    Fonction principale de l'interface.
    """
    while True:
        try:
            show_menu()
            choice = input("\n🔥 Votre choix (1-8): ").strip()
            
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
                run_automatic_performance_test()
                
            elif choice == '5':
                interactive_mode()
                
            elif choice == '6':
                show_samples()
                
            elif choice == '7':
                toggle_test_mode()
                
            elif choice == '8':
                print("\n👋 Au revoir!")
                break
                
            else:
                print("\n❌ Choix invalide. Veuillez entrer un nombre entre 1 et 8.")
                
            input("\n⏸️  Appuyez sur Entrée pour continuer...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            input("\n⏸️  Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()