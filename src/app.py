from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag import query_rag  # Wir importieren deine RAG-Funktion

# 1. Die App initialisieren
app = FastAPI(
    title="RAG Research Assistant API",
    description="Eine API, die PDFs analysiert und Fragen beantwortet.",
    version="1.0.0"
)

# 2. Datenmodell definieren (Der "Bestellzettel")
# Pydantic prüft, ob der Nutzer wirklich Text schickt und keine Zahlen oder Quatsch.
class QueryRequest(BaseModel):
    query: str

# 3. Der Endpunkt (Die "Tür" zur Küche)
@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    """
    Nimmt eine JSON-Anfrage entgegen: {"query": "Deine Frage"}
    Und gibt die Antwort der KI zurück.
    """
    user_question = request.query

    if not user_question:
        raise HTTPException(status_code=400, detail="Keine Frage gesendet!")

    print(f"📩 API Anfrage erhalten: {user_question}")

    # Hier rufen wir dein "Gehirn" auf (rag.py)
    response = query_rag(user_question)

    return {
        "question": user_question,
        "answer": response
    }

# 4. Ein einfacher Test-Endpunkt (Health Check)
@app.get("/")
def health_check():
    return {"status": "running", "message": "Der Server ist bereit! 🚀"}