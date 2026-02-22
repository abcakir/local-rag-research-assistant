"""
rag.py - Das "Gehirn" der Anwendung (RAG-Logik)

Diese Datei verbindet die Datenbank-Suche
mit der künstlichen Intelligenz (LLM).

Aufgaben:
1. Retrieval: Findet die passendsten Textstellen zur Frage des Nutzers in der ChromaDB.
2. Prompting: Baut einen strikten Prompt, der Halluzinationen verhindert.
3. Generation: Sendet Kontext + Frage an das LLM (Ollama/Mistral) und empfängt die Antwort.
4. Sourcing: Fügt die Quellenangaben (Dateinamen) zur Antwort hinzu.

Nutzt "Negative Constraints" im Prompt, um Fakten-Erfindung zu stoppen.
"""

import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

DATA_PATH = "./data"
DB_PATH = "./chroma_db"

PROMPT_TEMPLATE = """
Du bist ein strikter Analyse-Assistent.
Deine Aufgabe ist es, die Frage ausschließlich basierend auf dem folgenden Kontext zu beantworten.

REGELN:
1. Nutze NUR die Informationen aus dem Abschnitt "KONTEXT".
2. Nutze NIEMALS dein internes Wissen (keine Geografie, keine Geschichte, keine Fakten, die nicht im Text stehen).
3. Antworte sehr detailliert!
4. Wenn die Antwort nicht im Kontext steht, antworte exakt mit: "Diese Information ist im Dokument nicht enthalten."

Chatverlauf:
{history}

Kontext:
{context}

---

Frage: {question}
"""

def get_embedding_function():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def query_rag(query_text: str, history: list = []):
    """
    Hauptfunktion für die Anfrage.
    """
    # 1. Datenbank laden
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)

    # 2. Suchen
    print(f"🔍 Suche nach: '{query_text}'")
    results = db.similarity_search_with_score(query_text, k=5)

    # 3. Kontext zusammenbauen
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # 4. History formatieren
    formatted_history = ""
    for msg in history:
        role = "User" if msg.get('role') == 'user' else "Assistant"
        content = msg.get('content', '')
        formatted_history += f"{role}: {content}\n"

    # 5. Prompt erstellen
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(
        context=context_text,
        history=formatted_history,
        question=query_text
    )

    # 6. Modell initialisieren
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    print(f"🤖 Verbinde zu Ollama unter: {ollama_base_url}")

    model = ChatOllama(
        model="mistral",
        base_url=ollama_base_url,
        temperature=0  # keine Kreatitvität wenn 0
    )

    # 7. Antwort generieren
    response_message = model.invoke(prompt)
    response_text = response_message.content

    # 8. Quellen vorbereiten
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    unique_sources = list(set(sources))

    # 9. Ergebnis formatieren & Check auf "Nicht gefunden"
    if "Diese Information ist im Dokument nicht enthalten" in response_text:
        formatted_response = response_text
        print("❌ Info nicht gefunden -> Keine Quellen angezeigt.")
    else:
        formatted_response = f"{response_text}\n\nQuellen: {unique_sources}"
        print("✅ Antwort gefunden -> Quellen angehängt.")

    return formatted_response