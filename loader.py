import os
import fitz
import markdown
import json
from config import config

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
    data_dir = config.get_data_dir()
    markdown_dir = os.path.join(data_dir, config.markdown_subdir)
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
    data_dir = config.get_data_dir()
    root_dir = os.path.join(data_dir, config.pdf_subdir)
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
    data_dir = config.get_data_dir()
    json_filename = config.get_json_filename()
    json_file_path = os.path.join(data_dir, json_filename)
    
    if os.path.exists(json_file_path):
        content = load_file(json_file_path)
        if content:
            return {
                "source": json_file_path,
                "content": content
            }
    
    return None

def load_all_documents():
    """Charge tous les documents de tous les formats"""
    mode_text = "MODE TEST" if config.test_mode else "MODE PRODUCTION"
    data_dir = config.get_data_dir()
    print(f"Démarrage du chargement des documents - {mode_text}")
    print(f"Répertoire de données: {data_dir}")
    
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
        print("Fichier JSON chargé")
    else:
        print("Aucun fichier JSON trouvé")
    
    # Combiner toutes les données
    all_documents = []
    all_documents.extend(markdown_data)
    all_documents.extend(pdf_data)
    if json_data:
        all_documents.append(json_data)
    
    return all_documents
