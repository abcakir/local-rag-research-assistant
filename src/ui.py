import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"

# --- CONFIG & CSS ---
st.set_page_config(page_title="Document Intelligence", page_icon="📄", layout="wide")

st.markdown("""
    <style>
        /* Header Bereich verkleinern */
        .block-container {
            padding-top: 2rem;
        }
        /* Buttons professioneller gestalten */
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            font-weight: bold;
        }
        /* Chat Input Styling */
        .stChatInput {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("Document Intelligence Hub")
st.markdown("Interne Wissensdatenbank & Analyse")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: MANAGEMENT ---
with st.sidebar:
    st.header("Dateiverwaltung")

    # 1. UPLOAD
    with st.container():
        st.subheader("Upload")
        uploaded_file = st.file_uploader("PDF auswählen", type=["pdf"], label_visibility="collapsed")

        if uploaded_file is not None:
            if st.button("Verarbeiten", type="primary", use_container_width=True):
                with st.spinner("Dokument wird analysiert..."):
                    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                    try:
                        response = requests.post(f"{API_URL}/upload", files=files)
                        if response.status_code == 200:
                            st.toast(f"✅ '{uploaded_file.name}' erfolgreich integriert!", icon="✅")
                            time.sleep(1) # Kurz warten für UX
                            st.rerun()
                        else:
                            st.error(f"Fehler: {response.text}")
                    except Exception as e:
                        st.error(f"Verbindungsfehler: {e}")

    st.markdown("---")

    # 2. DATEILISTE
    st.subheader("Indexierte Dokumente")

    try:
        res = requests.get(f"{API_URL}/files")
        if res.status_code == 200:
            files = res.json().get("files", [])

            if files:
                for f in files:
                    col1, col2 = st.columns([0.7, 0.3])

                    with col1:
                        st.text(f"{f[:20]}..." if len(f) > 20 else f, help=f)

                    with col2:
                        if st.button("X", key=f"del_{f}", help="Dokument dauerhaft löschen"):
                            try:
                                del_res = requests.delete(f"{API_URL}/files/{f}")
                                if del_res.status_code == 200:
                                    st.toast(f"🗑️ '{f}' entfernt.", icon="🗑️")
                                    time.sleep(0.7)
                                    st.rerun()
                                else:
                                    st.error("Fehler")
                            except Exception as e:
                                st.error(f"Fehler: {e}")
            else:
                st.info("Keine Dokumente im Index.")

        else:
            st.warning("Server nicht erreichbar.")

    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")

    st.markdown("---")

    # Reset Button ganz unten
    if st.button("Chatverlauf leeren", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# --- HAUPTBEREICH: CHAT ---

# 1. Chatverlauf anzeigen
for message in st.session_state.messages:
    role = message["role"]
    avatar = "👤" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# 2. Input Feld
if prompt := st.chat_input("Stellen Sie eine Frage an die Dokumente..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Bot antwortet
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()

        with st.spinner("Analysiere Daten..."):
            try:
                payload = {
                    "query": prompt,
                    "history": st.session_state.messages[:-1]
                }

                response = requests.post(f"{API_URL}/chat", json=payload)

                if response.status_code == 200:
                    answer = response.json().get("answer")

                    not_found_phrases = ["keine informationen", "nicht im kontext", "weiß ich nicht"]
                    if any(p in answer.lower() for p in not_found_phrases):
                        st.warning("Keine passenden Informationen in den Dokumenten gefunden.")

                    message_placeholder.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    message_placeholder.error(f"Server Fehler: {response.status_code}")
            except Exception as e:
                message_placeholder.error(f"Verbindung fehlgeschlagen: {e}")