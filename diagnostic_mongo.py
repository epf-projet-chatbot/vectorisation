#!/usr/bin/env python3
"""
Script de diagnostic pour la connexion MongoDB
Aide à résoudre les problèmes d'authentification
"""

import os
from dotenv import load_dotenv

def check_env_variables():
    """Vérifie les variables d'environnement"""
    print("🔍 Vérification des variables d'environnement:")
    print("-" * 50)
    
    # Charger le fichier .env s'il existe
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ Fichier .env trouvé et chargé")
    else:
        print("⚠️  Fichier .env non trouvé")
    
    # Variables à vérifier
    required_vars = [
        'MONGO_URI', 'MONGO_HOST', 'MONGO_PORT', 
        'MONGO_USERNAME', 'MONGO_PASSWORD',
        'DATABASE_NAME', 'COLLECTION_NAME', 'API_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'API_KEY' in var:
                print(f"✅ {var}: ******* (masqué)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Non défini")

def test_mongodb_connection():
    """Teste différents types de connexions MongoDB"""
    print("\n🔗 Test de connexion MongoDB:")
    print("-" * 50)
    
    try:
        from mongo import init_connection, test_connection
        
        # Tenter la connexion
        if init_connection():
            print("✅ Initialisation réussie")
            
            # Test de ping
            if test_connection():
                print("✅ Test de ping réussi")
            else:
                print("❌ Test de ping échoué")
        else:
            print("❌ Échec de l'initialisation")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        
        # Suggestions de résolution
        print("\n💡 Suggestions de résolution:")
        print("1. Vérifiez que MongoDB est démarré")
        print("2. Vérifiez vos identifiants (MONGO_USER, MONGO_PASSWORD)")
        print("3. Vérifiez l'URI de connexion (MONGO_URI)")
        print("4. Assurez-vous que l'utilisateur a les permissions nécessaires")

def suggest_mongo_uri():
    """Suggère des formats d'URI MongoDB"""
    print("\n📝 Formats d'URI MongoDB courants:")
    print("-" * 50)
    
    print("1. MongoDB local avec authentification:")
    print("   MONGO_URI=mongodb://username:password@localhost:27017/database")
    
    print("\n2. MongoDB Atlas (cloud):")
    print("   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database")
    
    print("\n3. MongoDB Docker:")
    print("   MONGO_URI=mongodb://root:password@localhost:27017/database?authSource=admin")
    
    print("\n4. MongoDB sans authentification (développement):")
    print("   MONGO_URI=mongodb://localhost:27017/database")

def create_env_file():
    """Aide à créer un fichier .env"""
    print("\n📄 Création du fichier .env:")
    print("-" * 50)
    
    if os.path.exists('.env'):
        print("⚠️  Le fichier .env existe déjà")
        response = input("Voulez-vous le recréer? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Template de base
    env_template = """# Configuration MongoDB
MONGO_URI=mongodb://username:password@localhost:27017/database

# Ou utilisez des paramètres séparés:
# MONGO_HOST=localhost
# MONGO_PORT=27017
# MONGO_USER=your_username
# MONGO_PASSWORD=your_password

# Configuration de la base de données
DATABASE_NAME=chatbot_db
COLLECTION_NAME=data

# API Key pour Groq
API_KEY=your_groq_api_key_here

# Configuration des chunks
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ Fichier .env créé avec succès")
        print("📝 Modifiez-le avec vos vraies valeurs de connexion")
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")

def main():
    """Fonction principale"""
    print("🚀 DIAGNOSTIC MONGODB - CHATBOT JURIDIQUE")
    print("=" * 60)
    
    while True:
        print("\nOptions disponibles:")
        print("1. Vérifier les variables d'environnement")
        print("2. Tester la connexion MongoDB")
        print("3. Afficher les formats d'URI MongoDB")
        print("4. Créer un fichier .env template")
        print("5. Quitter")
        
        choice = input("\nVotre choix (1-5): ").strip()
        
        if choice == '1':
            check_env_variables()
        elif choice == '2':
            test_mongodb_connection()
        elif choice == '3':
            suggest_mongo_uri()
        elif choice == '4':
            create_env_file()
        elif choice == '5':
            print("👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide")
        
        input("\n⏸️  Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()
