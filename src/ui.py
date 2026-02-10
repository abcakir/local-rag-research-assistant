import streamlit as st
import requests

# Das ist die Adresse, wo dein FastAPI-Server läuft
# WICHTIG: Der Port (8000) muss mit dem von uvicorn übereinstimmen!
API_URL = "http://127.0.0.1:8000/chat"

# --- Seite konfigurieren ---
st.set_page_config(page_title="RAG Assistant", page_icon="🤖")

st.title("🧠 Mein AI Research Assistant")
st.write("Stelle eine Frage an deine hochgeladenen PDFs.")

# --- Eingabebereich ---
# Ein Textfeld für den Nutzer
user_input = st.text_area("Deine Frage:", placeholder="Was ist ein digitales Zertifikat?")

# --- Logik ---
if st.button("Frage senden 🚀"):
    if not user_input:
        st.warning("Bitte gib eine Frage ein!")
    else:
        # Ladebalken anzeigen, während die KI denkt
        with st.spinner("Die KI durchsucht die Dokumente..."):
            try:
                # 1. Anfrage an die API senden
                response = requests.post(API_URL, json={"query": user_input})

                # 2. Prüfen, ob alles geklappt hat (Status 200 = OK)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Keine Antwort erhalten.")

                    st.success("Antwort gefunden!")
                    st.markdown(answer)
                else:
                    st.error(f"Fehler vom Server: {response.status_code}")
                    st.text(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Verbindung fehlgeschlagen! ❌")
                st.info("Tipp: Läuft dein Backend-Server? (uvicorn src.app:app)")