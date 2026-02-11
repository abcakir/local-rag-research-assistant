import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG Assistant Pro", page_icon="🧠", layout="wide")

st.title("🧠 Mein AI Research Assistant Pro")

# --- SIDEBAR: DOKUMENTEN-MANAGEMENT ---
with st.sidebar:
    st.header("📂 Dokumente")
    uploaded_file = st.file_uploader("PDF hochladen", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Datei verarbeiten & Lernen 🧠"):
            with st.spinner("Lade hoch und lerne..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                try:
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success("Erfolgreich gelernt!")
                    else:
                        st.error(f"Fehler: {response.text}")
                except Exception as e:
                    st.error(f"Verbindungsfehler: {e}")

    st.markdown("---")

    # Der "Zusammenfassen" Button
    if st.button("📑 Dokument zusammenfassen"):
        with st.spinner("Erstelle Zusammenfassung..."):
            try:
                # Wir schicken einfach einen speziellen Prompt an die Chat-API
                payload = {"query": "Fasse den Inhalt der hochgeladenen Dokumente kurz und strukturiert zusammen."}
                response = requests.post(f"{API_URL}/chat", json=payload)

                if response.status_code == 200:
                    summary = response.json().get("answer")
                    st.info("Zusammenfassung:")
                    st.markdown(summary)
                else:
                    st.error("Konnte nicht zusammenfassen.")
            except Exception as e:
                st.error(f"Fehler: {e}")

# --- HAUPTBEREICH: CHAT ---
st.subheader("💬 Chat")
user_input = st.text_area("Deine Frage an das Dokument:", height=100)

if st.button("Frage senden 🚀"):
    if not user_input:
        st.warning("Bitte gib eine Frage ein!")
    else:
        with st.spinner("Die KI denkt nach..."):
            try:
                response = requests.post(f"{API_URL}/chat", json={"query": user_input})

                if response.status_code == 200:
                    answer = response.json().get("answer")

                    # Intelligente Prüfung auf "Nichts gefunden"
                    not_found_phrases = ["keine informationen", "nicht im kontext", "weiß ich nicht"]
                    if any(phrase in answer.lower() for phrase in not_found_phrases):
                        st.warning("⚠️ Keine passenden Infos im Dokument gefunden.")
                    else:
                        st.success("✅ Antwort gefunden!")

                    st.markdown(answer)
                else:
                    st.error(f"Server Fehler: {response.status_code}")
            except Exception as e:
                st.error(f"Verbindung fehlgeschlagen: {e}")