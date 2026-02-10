import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# --- KONFIGURATION ---
DATA_PATH = "./data"
DB_PATH = "./db"
OLLAMA_MODEL = "llama3"

PROMPT_TEMPLATE = """
Beantworte die Frage basierend auf dem folgenden Kontext:

{context}

---

Beantworte die Frage basierend auf dem obigen Kontext: {question}
"""

def get_embedding_function():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def add_to_chroma(chunks):
    """Speichert Chunks in der DB."""
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=get_embedding_function()
    )
    db.add_documents(chunks)
    print(f"✅ {len(chunks)} Chunks gespeichert.")

def query_rag(query_text):
    """
    1. Suche in der DB nach relevanten Chunks.
    2. Sende Chunks + Frage an Ollama.
    3. Gib Antwort zurück.
    """
    # 1. Datenbank vorbereiten
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)

    # 2. Suchen (Top 5 Treffer)
    print(f"🔍 Suche nach: '{query_text}'")
    results = db.similarity_search_with_score(query_text, k=5)

    if not results:
        print("❌ Nichts Relevantes gefunden.")
        return

    # 3. Kontext zusammenbauen
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # 4. Prompt erstellen
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # 5. An Ollama senden
    print("🤖 Generiere Antwort mit Ollama...")
    model = ChatOllama(model=OLLAMA_MODEL)
    response_text = model.invoke(prompt)

    # 6. Ergebnis ausgeben
    print("\n" + "="*50)
    print(f"ANTWORT:\n{response_text.content}")
    print("="*50)

    # Quellen anzeigen (für den CV wichtig!)
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    print(f"\n📚 Quellen: {list(set(sources))}")

# --- HELPER FÜR INGESTION ---
def load_documents():
    documents = []
    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(DATA_PATH, file)
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
    return documents

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    return text_splitter.split_documents(documents)

# --- HAUPTPROGRAMM ---
if __name__ == "__main__":
    # Kleines Menü zum Testen
    print("1. Datenbank neu erstellen (Ingest)")
    print("2. Frage stellen (Query)")
    choice = input("Wähle (1 oder 2): ")

    if choice == "1":
        docs = load_documents()
        if docs:
            chunks = split_text(docs)
            add_to_chroma(chunks)
    elif choice == "2":
        question = input("Deine Frage: ")
        query_rag(question)