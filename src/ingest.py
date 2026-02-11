import os
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
            # print(f"📄 Lade PDF: {file}...") # Optional: Weniger Spam im Terminal
            try:
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())
            except Exception as e:
                print(f"⚠️ Fehler beim Laden von {file}: {e}")
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
    print(f"✂️  {len(documents)} Dokumente in {len(chunks)} Chunks zerlegt.")
    return chunks

def ingest_docs():
    """
    1. Verbindet sich mit der Datenbank.
    2. Löscht ALLE alten Einträge (Reset).
    3. Speichert die aktuellen PDFs neu.
    """
    print("🔄 Starte Datenbank-Update...")

    # 1. Verbindung zur Datenbank herstellen
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=get_embedding_function()
    )

    # 2. Alte Daten löschen
    existing_ids = db.get()["ids"]

    if existing_ids:
        print(f"🧹 Lösche {len(existing_ids)} alte Einträge aus dem Gedächtnis...")
        # Wir löschen die Einträge, aber behalten die Ordner-Struktur
        # Das verhindert den Windows-Fehler!
        db.delete(ids=existing_ids)
    else:
        print("🧹 Datenbank war bereits leer.")

    # 3. Neue Daten Laden
    docs = load_documents()

    if docs:
        chunks = split_text(docs)
        print(f"💾 Speichere {len(chunks)} neue Wissens-Häppchen...")
        db.add_documents(chunks)
        print("✅ Update fertig!")
        return True
    else:
        print("⚠️ Keine PDFs mehr da. Datenbank ist jetzt leer.")
        return True

# Damit man es auch manuell testen kann
if __name__ == "__main__":
    ingest_docs()