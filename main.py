import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np
import os
from dotenv import load_dotenv
from groq import Groq

# Carrega chaves do arquivo .env automaticamente
load_dotenv()

st.set_page_config(page_title="Ficaqui - Inteligência Urbana", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOMIZAÇÃO VISUAL (UI/UX) ---
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

with st.sidebar:
    st.header("Configurações Avançadas Ficaqui AI")
    env_groq_key = os.getenv("GROQ_API_KEY", "")
    groq_key = st.text_input("🔑 Groq API Key", value=env_groq_key, type="password", help="Sua chave será lida do .env automaticamente. Se vazio, cole aqui.")
    st.markdown("---")
    st.markdown("**Status do Projeto:** MVP B2G em Operação.")

st.title("🏙️ Ficaqui: Ecossistema de Inteligência Urbana")
st.markdown("Plataforma B2G de mapeamento de desertos comerciais e direcionamento de políticas públicas.")
st.markdown("---")

# 1. MOCK DATA EXPANDIDO DE ARACAJU COM ALTA GRANULARIDADE
@st.cache_data
def load_data():
    np.random.seed(42)  # Para consistencia reload
    ruas = [
        "Calçadão João Pessoa", "Rua Itabaiana", "Rua Laranjeiras", "Rua Geru", "Praça Fausto Cardoso",
        "Rua São Cristóvão", "Rua Apodi", "Avenida Rio Branco", "Rua Capela", "Travessa José de Faro",
        "Rua Propriá", "Rua Santo Amaro", "Rua Japaratuba", "Praça General Valadão", "Avenida Barão de Maruim"
    ]
    lat_base, lon_base = -10.913, -37.052
    
    data = []
    # Gerando múltiplos imóveis por rua (granularidade alta)
    for i, rua in enumerate(ruas):
        num_imoveis = np.random.randint(4, 12)
        for j in range(num_imoveis):
            lat = lat_base + np.random.uniform(-0.008, 0.008)
            lon = lon_base + np.random.uniform(-0.008, 0.008)
            status = np.random.choice(["Alugado", "Disponível", "Abandonado/IPTU Atrasado"], p=[0.4, 0.3, 0.3])
            tipo = np.random.choice(["Loja Térrea", "Galpão", "Prédio Misto", "Sala Comercial"])
            iluminacao = np.random.choice(["Boa", "Regular", "Ruim/Inexistente"])
            fluxo = np.random.randint(500, 15000)
            
            # Imóveis alugados geram receita alta. Disponíveis podem zerar e os abandonados devem impostos
            if status == "Alugado":
                receita = np.random.randint(10000, 350000)
            else:
                receita = 0
                
            potencial = round(np.random.uniform(0.3, 0.95), 2)
            
            data.append({
                "id_espaco": f"IMOVEL-{str(i).zfill(2)}-{str(j).zfill(2)}",
                "rua": rua,
                "tipo": tipo,
                "lat": lat,
                "lon": lon,
                "status_aluguel": status,
                "iluminacao": iluminacao,
                "receita_gerada": receita,
                "fluxo_pessoas_dia": fluxo,
                "potencial_retrofit": potencial
            })
            
    return pd.DataFrame(data)

df = load_data()

# 2. MÉTRICAS PRINCIPAIS DA ÁREA
col1, col2, col3, col4 = st.columns(4)
total_imoveis = len(df)
abandonados = len(df[df['status_aluguel'] == 'Abandonado/IPTU Atrasado'])
taxa_vacancia = (len(df[df['status_aluguel'] != 'Alugado']) / total_imoveis) * 100

col1.metric("Total de Espaços", total_imoveis)
col2.metric("Ociosidade (Vacância/Desuso)", f"{taxa_vacancia:.1f}%")
col3.metric("Receita Fiscal/Vendas Estimada", f"R$ {df['receita_gerada'].sum()/1e6:.1f}M")
col4.metric("Pontos Cegos Públicos (Ilum. Ruim)", len(df[df['iluminacao'] == 'Ruim/Inexistente']))

st.markdown("---")

# 3. INTERFACE EM ABAS
tab1, tab2 = st.tabs(["📍 Mapa Georreferenciado & Interativo", "💬 Ficaqui AI Real (LLM Chatbot)"])

with tab1:
    st.subheader("Painel de Controle Espacial")
    
    # Filtros para detalhar e cruzar
    f_status = st.multiselect("Filtrar por Status de Ocupação", df['status_aluguel'].unique(), default=df['status_aluguel'].unique())
    df_filtrado = df[df['status_aluguel'].isin(f_status)]
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        m = folium.Map(location=[-10.913, -37.052], zoom_start=15, tiles="cartodbpositron")
        
        for i, row in df_filtrado.iterrows():
            # A cor agora determina o problema do imóvel
            color = 'red' if row['status_aluguel'] == 'Abandonado/IPTU Atrasado' else 'orange' if row['status_aluguel'] == 'Disponível' else 'green'
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=max(row['fluxo_pessoas_dia']/1800, 3), # Visibilidade por fluxo com min_radius
                popup=f"<b># {row['id_espaco']}</b>",
                tooltip=f"Clique para analisar {row['id_espaco']} na Barra Lateral",
                color=color,
                fill=True,
                fill_opacity=0.6,
            ).add_to(m)
            
        # O st_folium captura eventos de clique no web app
        st_data = st_folium(m, width="100%", height=550)
        
    with c2:
        st.subheader("🏢 Diagnóstico do Espaço")
        
        # Identificar imóvel clicado no mapa
        clicked_espaco = None
        if st_data and st_data.get("last_object_clicked"):
            lat_clicado = st_data["last_object_clicked"]["lat"]
            lon_clicado = st_data["last_object_clicked"]["lng"]
            
            # Cálculo de distância simples para achar o id_espaco na base
            dist = (df_filtrado['lat'] - lat_clicado)**2 + (df_filtrado['lon'] - lon_clicado)**2
            min_dist_idx = dist.idxmin()
            clicked_espaco = df_filtrado.loc[min_dist_idx]['id_espaco']
        
        # Default Index para o SelectBox (Atualiza baseado no clique)
        default_idx = 0
        if clicked_espaco:
            default_idx = int(df.index[df['id_espaco'] == clicked_espaco][0]) # Busca index absoluto
            
        espaco_selecionado = st.selectbox(
            "📍 Selecionado no Mapa:", 
            df['id_espaco'],
            index=default_idx
        )
        
        if espaco_selecionado:
            detalhe = df[df['id_espaco'] == espaco_selecionado].iloc[0]
            st.write(f"**Logradouro:** {detalhe['rua']}")
            st.write(f"**Tipologia Principal:** {detalhe['tipo']}")
            st.write(f"**Status de Aluguel:** {detalhe['status_aluguel']}")
            st.write(f"**Infra. de Iluminação:** {detalhe['iluminacao']}")
            st.write(f"**Fluxo Diário Estimado:** {detalhe['fluxo_pessoas_dia']} hab/dia")
            
            # DIAGNÓSTICO PROFUNDO DA IA (Mockado para o Overview Rápido)
            st.markdown("### 📊 Overview Rápido")
            
            if detalhe['status_aluguel'] != "Alugado":
                if detalhe['fluxo_pessoas_dia'] > 8000 and detalhe['iluminacao'] != "Boa":
                    diag = "🚨 O imóvel goza de fluxo altíssimo e comercialmente viável, porém o ambiente urbano oprime a locação noturna. Ação: Notificar proprietários para IPTU progressivo ou iluminar entorno."
                elif detalhe['status_aluguel'] == "Abandonado/IPTU Atrasado":
                    diag = "🏚️ Endividamento sobre o valor venal. O Fundo Imobiliário (FII Ficaqui) deve focar na desapropriação e aplicar retrofit misto (Loja Embaixo + Moradia Em Cima)."
                else:
                    diag = "🏢 Oportunidade Subutilizada. Falta atração orgânica pós-18h. Precisa ancorar empreendimentos mistos."
            else:
                if detalhe['receita_gerada'] > 150000:
                    diag = "💎 Motor Comercial Forte! Manter calçadas, segurança e iluminação em dia para não perder este lojista para shoppings fechados."
                else:
                    diag = "✅ Ativo locado e operante. Exige apenas manutenção básica da prefeitura."
            
            st.info(diag)

with tab2:
    st.subheader("Chatbot G2B: Inteligência Generativa sobre os Dados Urbanos")
    st.markdown("🤖 *Conectado ao Agente Urbano.* Pergunte à Inteligência Artificial sobre as discrepâncias, isenções, ou como resolver os desertos mapeados.")
    
    # Session State Chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá, Gestor! Sou a IA avançada do Projeto Ficaqui. Consigo cruzar todos os dados dos imóveis mapeados na tabela desta região. Como posso guiar suas Políticas Públicas hoje?"}
        ]

    chat_container = st.container(height=500, border=False)
    for msg in st.session_state.messages:
        with chat_container.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ex: Qual o resumo dos locais com iluminação ruim e fluxo alto?")
    
    if prompt:
        # Mostra pergunta do user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        # Resposta Via Hugging Face (InferenceClient)
        with chat_container.chat_message("assistant"):
            with st.spinner("Analisando microdados com a Nuvem..."):
                try:
                    # Amostrando o DF para que caiba no contexto do limite gratuito do modelo (Zephyr 7B)
                    df_sample = df[['rua', 'status_aluguel', 'iluminacao', 'fluxo_pessoas_dia']].sample(min(15, len(df)))
                    context = df_sample.to_json(orient='records')
                    
                    system_prompt = f"""Você é o Ficaqui AI, um Urbanista Sênior de Aracaju/Brasil orientando Prefeituras e Fundos de Investimentos (FII).
REGRAS OBRIGATÓRIAS:
1. IDIOMA ESTREITO: Responda EXCLUSIVAMENTE em Português do Brasil impecável. Jamais misture palavras em inglês (ex: NUNCA use "several", use "várias").
2. EVIDÊNCIAS: Cite os dados EXATOS do JSON fornecido (nome da rua específica, status de locação) para comprovar seus argumentos.
3. LÓGICA URBANÍSTICA CORRETA:
 - Imóveis "Alugados" com fluxo alto significam SUCESSO e VITALIDADE. Isso NÃO é um problema!
 - Espaços "Abandonado/IPTU Atrasado" com grande fluxo são OURO para Fundos Imobiliários atuarem com Retrofits (Uso Misto: comércio embaixo, moradia em cima).
 - Locais com "Iluminação Ruim" ou "Disponíveis" e sem fluxo exigem a força da Prefeitura (melhoria pública e incentivos fiscais/ISS) para atrair âncoras.
Microdados (Amostra): {context}"""

                    messages_hf = [{"role": "system", "content": system_prompt}]
                    for m in st.session_state.messages[-4:]:  # last 4
                        if m["role"] != "system":
                            messages_hf.append({"role": m["role"], "content": m["content"]})
                    
                    # Conectar à Groq
                    if not groq_key:
                        st.error("Por favor, preencha sua GROQ_API_KEY no arquivo .env ou na aba lateral.")
                        st.stop()
                        
                    client = Groq(api_key=groq_key)
                    
                    # Stream the real AI response usando Groq API
                    response = ""
                    stream = client.chat.completions.create(
                        model="llama-3.3-70b-versatile", # Modelo Oficial Llama 3.3 (Super estável)
                        messages=messages_hf,
                        max_tokens=2048,
                        stream=True,
                        temperature=0.6,
                    )
                    
                    placeholder = st.empty()
                    for chunk in stream:
                        if hasattr(chunk, 'choices') and chunk.choices:
                            delta = getattr(chunk.choices[0].delta, 'content', "") or ""
                            response += delta
                            placeholder.markdown(response + "▌")
                    placeholder.markdown(response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"Erro ao contatar API da Groq. Detalhes: {e}")
                    st.warning("💡 Verifique se a sua chave da Groq está correta no arquivo .env ou se você atingiu o limite de requisições.")
