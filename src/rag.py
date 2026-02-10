"""
RAG SERVICE (Retrieval Augmented Generation)

Zweck:
Diese Datei enthält die Logik für das Beantworten von Fragen (Inference).
Sie wird später von der API (app.py) importiert und genutzt.

Ablauf:
1. Empfängt eine Frage (Query).
2. Sucht in der ChromaDB nach relevanten Kontext-Schnipseln (Retrieval).
3. Baut einen Prompt für das LLM (Ollama).
4. Generiert die Antwort.
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
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
    """Erstellt den Vektor-Übersetzer (Singleton-Pattern)."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def query_rag(query_text):
    """
    Hauptfunktion für die Anfrage.
    Wird später von der API (app.py) aufgerufen.
    """
    # 1. Datenbank laden
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)

    # 2. Suchen
    print(f"🔍 Suche nach: '{query_text}'")
    results = db.similarity_search_with_score(query_text, k=5)

    if not results:
        print("❌ Nichts Relevantes gefunden.")
        return "Ich habe dazu keine Informationen gefunden."

    # 3. Kontext zusammenbauen
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # 4. Prompt erstellen
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # 5. An Ollama senden
    print("🤖 Generiere Antwort mit Ollama...")
    model = ChatOllama(model=OLLAMA_MODEL)
    response_text = model.invoke(prompt)

    # 6. Ergebnis formatieren
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"{response_text.content}\n\nQuellen: {list(set(sources))}"

    print("✅ Antwort generiert.")
    return formatted_response

# Nur zum schnellen Testen, falls man die Datei direkt ausführt
if __name__ == "__main__":
    antwort = query_rag("Was ist ein Zertifikat?")
    print(antwort)