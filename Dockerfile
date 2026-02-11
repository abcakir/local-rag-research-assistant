# Wir nutzen ein schlankes Python-Image
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# System-Tools für ChromaDB installieren
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den restlichen Code kopieren
COPY . .

# Ports für API (8000) und UI (8501) vormerken
EXPOSE 8000
EXPOSE 8501

# Der Standardbefehl (wird durch docker-compose überschrieben)
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]