import streamlit as st
import os

st.set_page_config(page_title="Ficaqui - Inteligência Urbana", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.header("⚙️ Configurações Avançadas AI")
    groq_key = st.text_input("🔑 Groq API Key", type="password", help="Insira um Token da Groq para conectar o Chatbot B2G.")
    if groq_key:
        st.session_state.groq_api_key = groq_key
    st.markdown("---")
    st.markdown("**Status do Projeto:** MVP B2G em Operação.")

from src.data_loader import load_data
from src.ui_metrics import render_metrics
from src.tab_map import render_map_tab
from src.tab_chat import render_chat_tab

def main():
    st.title("🏙️ Ficaqui: Ecossistema de Inteligência Urbana")
    st.markdown("Plataforma B2G de mapeamento de desertos comerciais e direcionamento de políticas públicas.")
    st.markdown("---")
    
    df = load_data()
    render_metrics(df)
    
    st.markdown("---")
    tab1, tab2 = st.tabs(["📍 Mapa Georreferenciado & Interativo", "💬 Ficaqui AI Real (LLM Chatbot)"])
    
    with tab1:
        render_map_tab(df)
        
    with tab2:
        render_chat_tab(df)

if __name__ == "__main__":
    main()
