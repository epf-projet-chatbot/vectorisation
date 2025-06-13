#!/usr/bin/env python3
"""
Guide d'utilisation des modes TEST/PRODUCTION
"""

def show_usage():
    """Affiche les différentes façons d'utiliser les modes"""
    print("🚀 GUIDE D'UTILISATION DES MODES RAG")
    print("=" * 50)
    
    print("\n📋 1. PIPELINE DE VECTORISATION")
    print("-" * 30)
    print("Mode TEST (données réduites):")
    print("   python3 pipeline.py --test")
    print("")
    print("Mode PRODUCTION (toutes les données):")
    print("   python3 pipeline.py")
    print("   python3 pipeline.py --prod")
    print("")
    print("Autres options utiles:")
    print("   python3 pipeline.py --test --clear-db     # Vide la base de test")
    print("   python3 pipeline.py --stats-only          # Affiche les stats")
    
    print("\n🧪 2. TESTS DE PERFORMANCE")
    print("-" * 30)
    print("Mode TEST:")
    print("   python3 rag_performance_test.py --test")
    print("")
    print("Mode PRODUCTION:")
    print("   python3 rag_performance_test.py")
    print("   python3 rag_performance_test.py --prod")
    
    print("\n🔄 3. BASCULEMENT DE MODE")
    print("-" * 30)
    print("Via script dédié:")
    print("   python3 switch_mode.py toggle")
    print("   python3 switch_mode.py show")
    print("")
    print("Via l'interface de test:")
    print("   python3 rag_performance_test.py")
    print("   # Choisir option 7")
    
    print("\n📊 4. VÉRIFICATION DU MODE ACTUEL")
    print("-" * 30)
    print("Afficher la configuration:")
    print("   python3 switch_mode.py show")
    print("")
    print("Statistiques de la base:")
    print("   python3 pipeline.py --stats-only")
    
    print("\n💡 5. EXEMPLES PRATIQUES")
    print("-" * 30)
    print("Workflow de développement:")
    print("   1. python3 pipeline.py --test --clear-db")
    print("   2. python3 rag_performance_test.py --test")
    print("")
    print("Workflow de production:")
    print("   1. python3 pipeline.py --prod --clear-db")
    print("   2. python3 rag_performance_test.py --prod")
    
    print("\n🗄️  6. BASES DE DONNÉES")
    print("-" * 30)
    print("Mode TEST:       chatbot_test_db.data")
    print("Mode PRODUCTION: chatbot_db.data")
    print("")
    print("Les deux modes utilisent des bases séparées")
    print("pour éviter la pollution des données.")

if __name__ == "__main__":
    show_usage()
