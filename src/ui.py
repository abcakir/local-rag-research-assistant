import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG Assistant Pro", page_icon="🧠", layout="wide")
st.title("🧠 Mein AI Research Assistant Pro")

# --- SIDEBAR: DATEI MANAGER ---
with st.sidebar:
    st.header("📂 Dokumente")

    # 1. Upload Bereich
    uploaded_file = st.file_uploader("Neues PDF hinzufügen", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Hinzufügen & Lernen 🧠"):
            with st.spinner("Lade hoch..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                try:
                    res = requests.post(f"{API_URL}/upload", files=files)
                    if res.status_code == 200:
                        st.success("Gespeichert!")
                        st.rerun() # Seite neu laden, um Liste zu aktualisieren
                    else:
                        st.error(f"Fehler: {res.text}")
                except Exception as e:
                    st.error(f"Verbindungsfehler: {e}")

    st.markdown("---")
    st.subheader("Gespeicherte Dateien:")

    # 2. Liste anzeigen & Löschen
    try:
        # Liste vom Backend holen
        res = requests.get(f"{API_URL}/files")
        if res.status_code == 200:
            files = res.json().get("files", [])

            if files:
                for f in files:
                    # Layout: Text links, Mülleimer rechts
                    col1, col2 = st.columns([0.8, 0.2])

                    with col1:
                        st.text(f"📄 {f}")

                    with col2:
                        # WICHTIG: Unique Key für jeden Button!
                        if st.button("🗑️", key=f"del_{f}", help="Löschen"):
                            with st.spinner("Lösche..."):
                                del_res = requests.delete(f"{API_URL}/files/{f}")
                                if del_res.status_code == 200:
                                    st.success("Weg!")
                                    st.rerun() # Seite neu laden
                                else:
                                    st.error("Fehler")
            else:
                st.info("Keine Dateien vorhanden.")
        else:
            st.warning("Konnte Dateiliste nicht laden.")
    except Exception as e:
        st.error(f"API nicht erreichbar. Läuft uvicorn? ({e})")

# --- HAUPTBEREICH: CHAT ---
st.subheader("💬 Chat")
user_input = st.text_area("Deine Frage an die Dokumente:", height=100)

col_ask, col_sum = st.columns([0.2, 0.8])

with col_ask:
    send_button = st.button("Frage senden 🚀")

with col_sum:
    sum_button = st.button("📑 Alles zusammenfassen")

# Logik für Zusammenfassen
if sum_button:
    with st.spinner("Erstelle Zusammenfassung..."):
        try:
            payload = {"query": "Fasse den Inhalt aller hochgeladenen Dokumente kurz und strukturiert zusammen."}
            res = requests.post(f"{API_URL}/chat", json=payload)
            if res.status_code == 200:
                st.info("Zusammenfassung:")
                st.markdown(res.json().get("answer"))
            else:
                st.error("Fehler beim Zusammenfassen.")
        except Exception as e:
            st.error(f"Fehler: {e}")

# Logik für Chat
if send_button:
    if not user_input:
        st.warning("Bitte gib eine Frage ein!")
    else:
        with st.spinner("Die KI denkt nach..."):
            try:
                response = requests.post(f"{API_URL}/chat", json={"query": user_input})
                if response.status_code == 200:
                    answer = response.json().get("answer")

                    not_found_phrases = ["keine informationen", "nicht im kontext", "weiß ich nicht"]
                    if any(p in answer.lower() for p in not_found_phrases):
                        st.warning("⚠️ Keine Infos gefunden.")
                    else:
                        st.success("✅ Antwort gefunden!")

                    st.markdown(answer)
                else:
                    st.error(f"Server Fehler: {response.status_code}")
            except Exception as e:
                st.error(f"Verbindung fehlgeschlagen: {e}")