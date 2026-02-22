# ⚡ End-to-End RAG Application

Eine minimalistische, lokale **RAG-Applikation** (Retrieval-Augmented Generation) zur Analyse von PDF-Dokumenten.

Das System ermöglicht es, PDFs hochzuladen und Fragen zum Inhalt zu stellen. Die Antworten werden durch ein lokales LLM (Mistral) generiert, basierend auf den tatsächlich gefundenen Textstellen im Dokument – **ohne Halluzinationen** und **ohne Daten-Upload in die Cloud**.

![App Screenshot](https://i.imgur.com/ougv3h1.png)


---

## 🚀 Tech Stack

* **Backend:** FastAPI (Python)
* **Frontend:** Streamlit
* **AI/ML:** LangChain, Ollama (Mistral), HuggingFace Embeddings
* **Datenbank:** ChromaDB (Vektordatenbank)
* **Container:** Docker & Docker Compose

---

## 🛠️ Voraussetzungen

Bevor du startest, stelle sicher, dass folgende Tools installiert sind:

1.  **Docker & Docker Compose** (für die Container-Umgebung)
2.  **Ollama** (muss lokal auf deinem Rechner laufen)

### Ollama Setup (Wichtig!)
Da das LLM lokal läuft, muss Ollama auf deinem Host-System gestartet sein:

1.  Installiere [Ollama](https://ollama.com/).
2.  Lade das Modell herunter:
    ```bash
    ollama pull mistral
    ```
3.  Starte den Server (falls er nicht läuft):
    ```bash
    ollama serve
    ```

---

## 🏁 Starten der Anwendung

Das gesamte System (Backend + Frontend) lässt sich mit einem einzigen Befehl starten:

```bash
docker compose up --build
