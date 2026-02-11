import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from src.rag import query_rag
from src.ingest import ingest_docs

# Initialisierung
app = FastAPI(
    title="RAG Research Assistant API",
    description="Eine API, die PDFs analysiert und Fragen beantwortet.",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str

# --- 1. HEALTH CHECK ---
@app.get("/")
def health_check():
    return {"status": "running", "message": "Der Server ist bereit! 🚀"}

# --- 2. DATEIEN AUFLISTEN ---
@app.get("/files")
def list_files():
    """Zeigt alle PDFs im data-Ordner an."""
    if not os.path.exists("./data"):
        return {"files": []}
    files = [f for f in os.listdir("./data") if f.endswith(".pdf")]
    return {"files": files}

# --- 3. UPLOAD ---
@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Nur PDF-Dateien erlaubt!")

    os.makedirs("./data", exist_ok=True)
    save_path = f"./data/{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"📂 Datei gespeichert: {file.filename}. Starte Ingestion...")
    # Wir löschen die alte DB und lernen ALLES neu (damit alles synchron ist)
    success = ingest_docs()

    if success:
        return {"message": f"Datei '{file.filename}' verarbeitet!", "filename": file.filename}
    else:
        raise HTTPException(status_code=500, detail="Fehler bei der Ingestion.")

# --- 4. LÖSCHEN ---
@app.delete("/files/{filename}")
def delete_file(filename: str):
    """Löscht eine Datei und aktualisiert die Datenbank."""
    file_path = os.path.join("./data", filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path) # Datei löschen
            print(f"🗑️ Datei gelöscht: {filename}. Aktualisiere Datenbank...")

            # Datenbank neu aufbauen (ohne die gelöschte Datei)
            ingest_docs()

            return {"message": f"Datei '{filename}' gelöscht."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fehler beim Löschen: {e}")
    else:
        raise HTTPException(status_code=404, detail="Datei nicht gefunden.")

# --- 5. CHAT ---
@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    user_question = request.query
    if not user_question:
        raise HTTPException(status_code=400, detail="Keine Frage gesendet!")

    print(f"📩 Frage: {user_question}")
    response = query_rag(user_question)
    return {"question": user_question, "answer": response}