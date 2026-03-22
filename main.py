import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Ficaqui - Inteligência Urbana", layout="wide")

st.title("🏙️ Ficaqui: Dashboard de Revitalização Urbana")
st.markdown("---")

# 2. MOCK DATA (Dados Reais/Estimados de Aracaju - Março 2026)
@st.cache_data
def load_data():
    data = {
        'rua': ['Calçadão João Pessoa', 'Rua Itabaiana', 'Rua Laranjeiras', 'Rua Geru', 'Praça Fausto Cardoso'],
        'lat': [-10.9125, -10.9135, -10.9115, -10.9145, -10.9155],
        'lon': [-37.0515, -37.0525, -37.0505, -37.0535, -37.0545],
        'vacancia': [12, 45, 18, 55, 5], # % de imóveis fechados
        'fluxo_diario': [15000, 4000, 12000, 3000, 8000], # Pessoas/dia (SMTT)
        'crimes_mes': [35, 12, 28, 42, 8],
        'potencial_retrofit': [0.85, 0.40, 0.70, 0.30, 0.95] # Score de investimento
    }
    return pd.DataFrame(data)

df = load_data()

# 3. SIDEBAR - CONTROLE DO GESTOR
st.sidebar.header("Painel de Controle")
intervencao = st.sidebar.selectbox("Tipo de Intervenção", ["Retrofit Residencial", "Hub Comercial", "Segurança Tática"])
orcamento = st.sidebar.slider("Orçamento Estimado (R$ Milhões)", 0.5, 10.0, 2.5)

# 4. MÉTRICAS PRINCIPAIS (O Choque Econômico)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Vacância Média", f"{df['vacancia'].mean():.1f}%", "-2.5%")
col2.metric("Potencial de Receita (IPTU)", "R$ 4.2M", "+12%")
col3.metric("Pessoas Impactadas", f"{df['fluxo_diario'].sum()}", "Diário")
col4.metric("Score FII", "7.8/10", "Investimento")

st.markdown("---")

# 5. MAPA DE CALOR E ANÁLISE ESPACIAL
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📍 Mapa de Oportunidades (Centro de Aracaju)")
    # Criando o mapa centralizado no Centro
    m = folium.Map(location=[-10.913, -37.052], zoom_start=16, tiles="cartodbpositron")
    
    for i, row in df.iterrows():
        # Cor baseada na vacância (Vermelho = Crítico)
        color = 'red' if row['vacancia'] > 30 else 'orange' if row['vacancia'] > 15 else 'green'
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['fluxo_diario']/1000 * 2, # Tamanho pelo fluxo
            popup=f"Rua: {row['rua']}<br>Vacância: {row['vacancia']}%",
            color=color,
            fill=True,
        ).add_to(m)
    
    st_folium(m, width=800, height=450)

with c2:
    st.subheader("🤖 Insights da I.A. (Ficaqui AI)")
    
    # Simulação de Raciocínio da I.A. (AI Predictor)
    def ai_predictor(row):
        acao = "Isenção de ISS para café/coworking" if row['fluxo_diario'] >= 3000 else "Incentivo a Retrofit Residencial (Moradia de Uso Misto)"
        return f"Ação sugerida: {acao} nesta rua ({row['rua']}) devido à vacância de {row['vacancia']}%."

    rua_critica = df.sort_values(by='vacancia', ascending=False).iloc[0]
    
    st.info(f"**Análise de Prioridade: {rua_critica['rua']}**")
    st.write(f"""
    - **Diagnóstico:** Vacância Crítica ({rua_critica['vacancia']}%). Fluxo de pedestres ({rua_critica['fluxo_diario']} pessoas/dia) subutilizado.
    - **Causa provável:** Esvaziamento após as 18h e redução na segurança.
    - **Recomendação da IA:** {ai_predictor(rua_critica)}
    - **Impacto FII:** Potencial de valorizacão e reocupação urbana com base na demanda de habitação mista.
    """)
    
    # Gráfico de Radar ou Barras
    fig = px.bar(df, x='rua', y='vacancia', color='vacancia', title="Vacância por Logradouro")
    st.plotly_chart(fig, use_container_width=True)

# 6. PORTAL DO INVESTIDOR (Fundo Ficaqui)
st.markdown("---")
st.subheader("💰 Simulador de Viabilidade - Fundo FII (Banese)")
inv_col1, inv_col2 = st.columns(2)

with inv_col1:
    building_cost = st.number_input("Custo de Aquisição/Reforma (R$)", value=1200000)
    rent_target = st.number_input("Aluguel Alvo p/ m² (R$)", value=45)

with inv_col2:
    roi = ( (rent_target * 100 * 12) / building_cost ) * 100 # Exemplo simples
    st.metric("ROI Estimado (Anual)", f"{roi:.2f}%")
    st.progress(min(roi/20, 1.0))

st.success("✅ Este projeto é viável para captação via FII Ficaqui.")