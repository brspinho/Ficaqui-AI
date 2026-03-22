import streamlit as st

def render_metrics(df):
    col1, col2, col3, col4 = st.columns(4)
    total_imoveis = len(df)
    abandonados = len(df[df['status_aluguel'] == 'Abandonado'])
    taxa_vacancia = (len(df[df['status_aluguel'] != 'Alugado']) / total_imoveis) * 100

    col1.metric("Total de Espaços", total_imoveis)
    col2.metric("Ociosidade (Vacância/Desuso)", f"{taxa_vacancia:.1f}%")
    col3.metric("Receita Fiscal/Vendas Estimada", f"R$ {df['receita_gerada'].sum()/1e6:.1f}M")
    col4.metric("Pontos Cegos Públicos (Ilum. Ruim)", len(df[df['iluminacao'] == 'Ruim/Inexistente']))
    st.markdown("---")
