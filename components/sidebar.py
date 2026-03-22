import streamlit as st
import os

def render_sidebar():
    with st.sidebar:
        st.header("Configurações Avançadas Ficaqui AI")
        env_groq_key = os.getenv("GROQ_API_KEY", "")
        groq_key = st.text_input(
            "🔑 Groq API Key", 
            value=env_groq_key, 
            type="password", 
            help="Sua chave será lida do .env automaticamente. Se vazio, cole aqui."
        )
        st.markdown("---")
        st.markdown("**Status do Projeto:** MVP B2G em Operação.")
        return groq_key
