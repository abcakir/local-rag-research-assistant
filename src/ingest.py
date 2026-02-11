"""
INGESTION PIPELINE (ETL - Extract, Transform, Load)

Zweck:
Diese Datei ist für die VORBEREITUNG der Daten zuständig.
Sie muss nur ausgeführt werden, wenn neue PDFs in den 'data/'-Ordner gelegt wurden.

Ablauf:
1. Load: Liest PDFs aus dem Ordner.
2. Split: Zerlegt Texte in kleine Häppchen (Chunks).
3. Store: Berechnet Embeddings und speichert sie in ChromaDB.
"""

import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from src.rag import get_embedding_function, DATA_PATH, DB_PATH

def load_documents():
    """Liest alle PDFs aus dem data-Ordner."""
    documents = []
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(DATA_PATH, file)
            print(f"📄 Lade PDF: {file}...")
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
    return documents

def split_text(documents):
    """Schneidet Dokumente in kleine Häppchen."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✂️  Dokumente in {len(chunks)} Chunks zerlegt.")
    return chunks

def save_to_chroma(chunks):
    """Speichert die Chunks in der Vektor-Datenbank."""
    # Alte Datenbank löschen (für sauberen Neustart)
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    # Neue Datenbank erstellen
    db = Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_function(),
        persist_directory=DB_PATH
    )
    print(f"✅ Datenbank neu erstellt in {DB_PATH} mit {len(chunks)} Einträgen.")

def ingest_docs():
    """
    Führt die komplette Pipeline aus: Laden -> Splitten -> Speichern.
    Gibt True zurück, wenn es geklappt hat.
    """
    print("🔄 Starte Ingestion via API...")
    docs = load_documents()
    if not docs:
        print("⚠️ Keine Dokumente gefunden.")
        return False

    chunks = split_text(docs)
    save_to_chroma(chunks)
    return True

def main():
    print("🚀 Starte Ingestion-Pipeline...")
    docs = load_documents()
    if docs:
        chunks = split_text(docs)
        save_to_chroma(chunks)
    else:
        print("❌ Keine PDFs im 'data' Ordner gefunden!")

if __name__ == "__main__":
    main()