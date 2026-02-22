"""
🖥️ ui.py - Das Frontend (Minimal Version)
-----------------------------------------
Eine absolut reduzierte Benutzeroberfläche.
Fokus: Datei hochladen & Chatten. Keine Ablenkungen.
"""

import streamlit as st
import requests
import os

# Konfiguration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="RAG Chat", page_icon="🤖")
st.title("RAG Chat")

# --- SIDEBAR: DATEIEN ---
with st.sidebar:
    st.header("Dokumente")

    # 1. Upload
    uploaded_file = st.file_uploader("PDF hochladen", type="pdf")
    if uploaded_file and st.button("Hochladen"):
        with st.spinner("Lade..."):
            files = {"file": uploaded_file}
            res = requests.post(f"{API_URL}/upload", files=files)
            if res.status_code == 200:
                st.success("Gespeichert!")
                st.rerun()
            else:
                st.error("Fehler beim Upload.")

    st.divider()

    # 2. Dateiliste
    st.subheader("Im Index:")
    try:
        res = requests.get(f"{API_URL}/files")
        files = res.json().get("files", [])
        for f in files:
            # Name + Löschen-Button
            col1, col2 = st.columns([0.8, 0.2])
            col1.caption(f)
            if col2.button("X", key=f):
                requests.delete(f"{API_URL}/files/{f}")
                st.rerun()

        if not files:
            st.caption("Keine Dateien.")
    except:
        st.error("Backend offline.")

    # 3. Reset
    if st.button("Chat leeren", type="primary"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT BEREICH ---

# Session State initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = []

# 1. Verlauf anzeigen
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 2. Eingabe & Antwort
if prompt := st.chat_input("Frage stellen..."):
    # User-Nachricht sofort anzeigen
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Anfrage an API
    try:
        payload = {"query": prompt, "history": st.session_state.messages[:-1]}

        with st.spinner("Denke nach..."):
            response = requests.post(f"{API_URL}/chat", json=payload)

            if response.status_code == 200:
                answer = response.json().get("answer")

                # Antwort anzeigen & speichern
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.chat_message("assistant").write(answer)
            else:
                st.error(f"Server-Fehler: {response.status_code}")

    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")