import os
import fitz
import markdown
import json

DATA_DIR = "./data"

def load_file(path):
    """Charge un fichier selon son extension"""
    ext = os.path.splitext(path)[-1]
    
    if ext == ".pdf":
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    
    with open(path, "r", encoding="utf-8") as f:
        if ext == ".md":
            return markdown.markdown(f.read())
        elif ext == ".json":
            return json.load(f)
    
    return None

def process_markdown_files():
    """Charge tous les fichiers markdown du dossier kiwiXlegal"""
    markdown_dir = os.path.join(DATA_DIR, "kiwiXlegal")
    markdown_data = []
    
    if os.path.exists(markdown_dir):
        for filename in os.listdir(markdown_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(markdown_dir, filename)
                content = load_file(file_path)
                if content:
                    markdown_data.append({
                        "source": file_path,
                        "content": content
                    })
    
    return markdown_data

def process_pdf_files():
    """Charge tous les fichiers PDF en parcourant récursivement le dossier root"""
    root_dir = os.path.join(DATA_DIR, "root")
    pdf_data = []
    
    if os.path.exists(root_dir):
        for root, dirs, files in os.walk(root_dir):
            for filename in files:
                if filename.endswith(".pdf"):
                    file_path = os.path.join(root, filename)
                    content = load_file(file_path)
                    if content:
                        pdf_data.append({
                            "source": file_path,
                            "content": content
                        })
    
    return pdf_data

def process_json_file():
    """Charge le fichier JSON dans le dossier data"""
    data_dir = DATA_DIR
    json_data = None
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(data_dir, filename)
                content = load_file(file_path)
                if content:
                    json_data = {
                        "source": file_path,
                        "content": content
                    }
                break  # Prendre seulement le premier JSON trouvé
    
    return json_data

def load_all_documents():
    """Charge tous les documents de tous les formats"""
    print("Démarrage du chargement des documents...")
    
    # Charger les fichiers markdown
    print("Chargement des fichiers markdown...")
    markdown_data = process_markdown_files()
    print(f"✓ {len(markdown_data)} fichiers markdown chargés")
    
    # Charger les fichiers PDF
    print("Chargement des fichiers PDF...")
    pdf_data = process_pdf_files()
    print(f"✓ {len(pdf_data)} fichiers PDF chargés")
    
    # Charger le fichier JSON
    print("Chargement du fichier JSON...")
    json_data = process_json_file()
    if json_data:
        print("✓ Fichier JSON chargé")
    else:
        print("⚠ Aucun fichier JSON trouvé")
    
    # Combiner toutes les données
    all_documents = []
    all_documents.extend(markdown_data)
    all_documents.extend(pdf_data)
    if json_data:
        all_documents.append(json_data)
    
    return all_documents

DATA_DIR = "./data"

def process_markdown_files():
    """Charge tous les fichiers markdown du dossier kiwiXlegal"""
    markdown_dir = os.path.join(DATA_DIR, "kiwiXlegal")
    markdown_data = []
    
    if os.path.exists(markdown_dir):
        for filename in os.listdir(markdown_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(markdown_dir, filename)
                content = load_file(file_path)
                if content:
                    markdown_data.append({
                        "source": file_path,
                        "content": content
                    })
    
    return markdown_data

def process_pdf_files():
    """Charge tous les fichiers PDF en parcourant récursivement le dossier root"""
    root_dir = os.path.join(DATA_DIR, "root")
    pdf_data = []
    
    if os.path.exists(root_dir):
        for root, dirs, files in os.walk(root_dir):
            for filename in files:
                if filename.endswith(".pdf"):
                    file_path = os.path.join(root, filename)
                    content = load_file(file_path)
                    if content:
                        pdf_data.append({
                            "source": file_path,
                            "content": content
                        })
    
    return pdf_data

def process_json_file():
    """Charge le fichier JSON dans le dossier data"""
    data_dir = DATA_DIR
    json_data = None
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(data_dir, filename)
                content = load_file(file_path)
                if content:
                    json_data = {
                        "source": file_path,
                        "content": content
                    }
                break  # Prendre seulement le premier JSON trouvé
    
    return json_data

def run_pipeline():
    """Exécute la pipeline complète de chargement des données"""
    print("Démarrage de la pipeline de chargement...")
    
    # Charger les fichiers markdown
    print("Chargement des fichiers markdown...")
    markdown_data = process_markdown_files()
    print(f"✓ {len(markdown_data)} fichiers markdown chargés")
    
    # Charger les fichiers PDF
    print("Chargement des fichiers PDF...")
    pdf_data = process_pdf_files()
    print(f"✓ {len(pdf_data)} fichiers PDF chargés")
    
    # Charger le fichier JSON
    print("Chargement du fichier JSON...")
    json_data = process_json_file()
    if json_data:
        print("✓ Fichier JSON chargé")
    else:
        print("⚠ Aucun fichier JSON trouvé")
    
    # Retourner toutes les données
    return {
        "markdown": markdown_data,
        "pdf": pdf_data,
        "json": json_data
    }

if __name__ == "__main__":
    data = run_pipeline()
    print(f"\nRésumé du chargement:")
    print(f"- Fichiers markdown: {len(data['markdown'])}")
    print(f"- Fichiers PDF: {len(data['pdf'])}")
    print(f"- Fichier JSON: {'Oui' if data['json'] else 'Non'}")