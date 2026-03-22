import streamlit as st
import os

def render_sidebar():
    with st.sidebar:
        st.header("Ficaqui")
        st.subheader("Sistema Inteligente de Revitalização Comercial")
        
        st.markdown("---")
        
        st.markdown("### Navegação")
        st.info("Utilize as abas superiores para alternar entre as visões do sistema.")
        
        st.markdown("---")
        
        st.markdown("### Suporte Técnico")
        st.write("Em caso de dúvidas, consulte a documentação ou acesse o chat de IA.")
        
        st.markdown("---")
        st.caption("Versão 2.1.0 - Hackathon 2026")
