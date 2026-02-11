import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from src.rag import query_rag
from src.ingest import ingest_docs

# 1. Die App initialisieren
app = FastAPI(
    title="RAG Research Assistant API",
    description="Eine API, die PDFs analysiert und Fragen beantwortet.",
    version="1.0.0"
)

# 2. Datenmodell definieren
class QueryRequest(BaseModel):
    query: str

@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    """
    Nimmt eine PDF-Datei entgegen, speichert sie und startet das Lernen.
    """
    # 1. Prüfen, ob es ein PDF ist
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Nur PDF-Dateien erlaubt!")

    # 2. Datei speichern
    # Wir stellen sicher, dass der data-Ordner existiert
    os.makedirs("./data", exist_ok=True)

    save_path = f"./data/{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Datenbank neu aufbauen (Ingestion triggern)
    print(f"📂 Datei gespeichert: {file.filename}. Starte Ingestion...")
    success = ingest_docs()

    if success:
        return {"message": f"Datei '{file.filename}' erfolgreich verarbeitet!", "filename": file.filename}
    else:
        raise HTTPException(status_code=500, detail="Fehler bei der Verarbeitung der Datei.")


# 3. Der Chat Endpunkt
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

    response = query_rag(user_question)

    return {
        "question": user_question,
        "answer": response
    }

# 4. Health Check
@app.get("/")
def health_check():
    return {"status": "running", "message": "Der Server ist bereit! 🚀"}