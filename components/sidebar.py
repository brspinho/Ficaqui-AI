import streamlit as st
import os

def render_sidebar():
    with st.sidebar:
        st.header("Painel de Planejamento")
        st.markdown("Configure os parâmetros de intervenção urbana abaixo.")
        
        st.subheader("Metas de Intervenção")
        ocupacao_meta = st.slider("Meta de Ocupação Comercial (%)", 50, 100, 85)
        
        st.subheader("Zonas de Prioridade")
        prioridade = st.multiselect(
            "Priorizar Áreas:",
            ["Calçadões", "Grandes Avenidas", "Zonas de Retrofit", "Áreas de Segurança"],
            default=["Calçadões", "Zonas de Retrofit"]
        )
        
        st.subheader("Cenários Habilitados")
        retrofit_mode = st.toggle("Ativar Modo Retrofit (Uso Misto)", value=True)
        incentivo_noturno = st.toggle("Incentivo para Operação Noturna", value=False)
        
        st.markdown("---")
        st.markdown("**Status do Projeto:** Inteligência de Planejamento Ativa.")
        
        # O retorno agora pode ser um dicionário de parâmetros de planejamento
        return {
            "ocupacao_meta": ocupacao_meta,
            "prioridade": prioridade,
            "retrofit_mode": retrofit_mode,
            "incentivo_noturno": incentivo_noturno
        }
