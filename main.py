import streamlit as st
from dotenv import load_dotenv
import os

# Import modules
from utils.css import inject_custom_css
from components.sidebar import render_sidebar
from components.metrics import render_metrics
from data.loader import load_data
from views.map_view import render_map_view
from views.chat_view import render_chat_view
from views.report_view import render_report_view

# Carrega chaves do arquivo .env automaticamente
load_dotenv()

st.set_page_config(
    page_title="Ficaqui - Sistema Inteligente de Revitalização Comercial", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Injeta CSS personalizado
inject_custom_css()

# Renderiza Sidebar
render_sidebar()

# Recupera a chave da Groq do ambiente
groq_key = os.getenv("GROQ_API_KEY")

# Cabeçalho Principal
st.title("Ficaqui: Sistema Inteligente de Revitalização Comercial")
st.markdown("Plataforma B2G de mapeamento de desertos comerciais e direcionamento de políticas públicas.")
st.markdown("---")

# Carrega os dados (cacheado)
df = load_data()

# Renderiza as métricas globais
render_metrics(df)

# Cria as abas de interface
tab1, tab2, tab3 = st.tabs([
    "Mapa Georreferenciado e Interativo", 
    "Ficaqui AI (Chatbot)",
    "Relatórios Executivos e Exportação"
])

# Renderiza as Views para cada Aba
with tab1:
    render_map_view(df)

with tab2:
    render_chat_view(df, groq_key)

with tab3:
    render_report_view(df, groq_key)
