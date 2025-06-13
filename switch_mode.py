#!/usr/bin/env python3
"""
Script pour basculer entre mode test et production
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire courant au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def toggle_mode():
    """Bascule entre test et production"""
    from config import config
    
    current_mode = "TEST" if config.test_mode else "PRODUCTION"
    new_mode = "PRODUCTION" if config.test_mode else "TEST"
    
    print(f"🔄 Mode actuel: {current_mode}")
    print(f"   Base actuelle: {config.get_database_name()}")
    
    # Modifier le fichier .env
    env_path = '.env'
    if not os.path.exists(env_path):
        print("❌ Fichier .env non trouvé")
        return False
    
    # Lire le fichier
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Modifier TEST_MODE
    new_test_mode = "false" if config.test_mode else "true"
    
    for i, line in enumerate(lines):
        if line.startswith('TEST_MODE='):
            lines[i] = f'TEST_MODE={new_test_mode}\n'
            break
    else:
        lines.append(f'TEST_MODE={new_test_mode}\n')
    
    # Écrire le fichier
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Basculé vers mode {new_mode}")
    
    # Recharger la config pour afficher le nouveau mode
    from config import VectorizationConfig
    new_config = VectorizationConfig.from_env()
    print(f"   Nouvelle base: {new_config.get_database_name()}")
    
    return True

def show_current_mode():
    """Affiche le mode actuel"""
    from config import config
    
    mode = "TEST" if config.test_mode else "PRODUCTION"
    db_name = config.get_database_name()
    
    print(f"📊 Mode actuel: {mode}")
    print(f"📊 Base de données: {db_name}")
    print(f"📊 Collection: {config.get_collection_name()}")

def main():
    """Fonction principale"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['toggle', 'switch', 'bascule']:
            toggle_mode()
        elif command in ['show', 'status', 'afficher']:
            show_current_mode()
        else:
            print("Usage:")
            print(f"  {sys.argv[0]} toggle  - Bascule entre test/production")
            print(f"  {sys.argv[0]} show    - Affiche le mode actuel")
    else:
        print("🚀 GESTIONNAIRE DE MODE RAG")
        print("=" * 30)
        print("1. Afficher le mode actuel")
        print("2. Basculer le mode")
        print("3. Quitter")
        
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == '1':
            show_current_mode()
        elif choice == '2':
            toggle_mode()
        elif choice == '3':
            print("👋 Au revoir!")
        else:
            print("❌ Choix invalide")

if __name__ == "__main__":
    main()
