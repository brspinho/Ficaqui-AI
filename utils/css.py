import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        /* Tipografia de Cabeçalhos em Azul Esverdeado */
        h1, h2, h3 {
            color: #00796B !important;
            font-family: 'Inter', sans-serif;
        }
        
        /* Cartões de Métrica Premium (Dashboard Vibe) */
        div[data-testid="metric-container"] {
            background-color: #FFFFFF;
            border-radius: 12px;
            border-left: 6px solid #009688; /* Azul Esverdeado (Confiança) */
            border-right: 4px solid #FFC107; /* Amarelo Dourado (Calor) */
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            padding: 15px 20px;
            transition: transform 0.2s ease-in-out;
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-4px);
        }
        
        /* Chatbot Bubbles mais modernas e com sobra leve */
        [data-testid="stChatMessage"] {
            background-color: #FFFFFF;
            border: 1px solid #EAEFEF;
            border-radius: 10px;
            padding: 15px;
        }
        
        /* Personalização da Scrollbar para não ficar cinza padrão */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #B2DFDB; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #009688; }
    </style>
    """, unsafe_allow_html=True)
