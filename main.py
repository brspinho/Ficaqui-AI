import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Ficaqui - Inteligência Urbana", layout="wide", initial_sidebar_state="expanded")

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

col1.metric("Total de Espaços Mapeados", total_imoveis)
col2.metric("Ociosidade (Vacância/Desuso)", f"{taxa_vacancia:.1f}%")
col3.metric("Receita Fiscal/Vendas Atual", f"R$ {df['receita_gerada'].sum()/1e6:.1f}M")
col4.metric("Pontos Cegos Públicos (Ilum. Ruim)", len(df[df['iluminacao'] == 'Ruim/Inexistente']))

st.markdown("---")

# 3. INTERFACE EM ABAS
tab1, tab2 = st.tabs(["📍 Mapa Georreferenciado & Diagnóstico Individual", "💬 Ficaqui AI (Chatbot Educacional/Gestor)"])

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
                radius=row['fluxo_pessoas_dia']/1800, # Visibilidade por fluxo
                popup=f"<b># {row['id_espaco']}</b><br>Rua: {row['rua']}<br>Status: {row['status_aluguel']}<br>Luz Pub: {row['iluminacao']}<br>Receita: R$ {row['receita_gerada']:,}",
                color=color,
                fill=True,
                fill_opacity=0.6,
            ).add_to(m)
            
        st_folium(m, width="100%", height=550)
        
    with c2:
        st.subheader("🏢 Diagnóstico Geral por Espaço")
        espaco_selecionado = st.selectbox("Selecione um identificador de imóvel no painel ou procure aqui:", df['id_espaco'])
        
        if espaco_selecionado:
            detalhe = df[df['id_espaco'] == espaco_selecionado].iloc[0]
            st.write(f"**Logradouro:** {detalhe['rua']}")
            st.write(f"**Tipologia Principal:** {detalhe['tipo']}")
            st.write(f"**Status de Aluguel:** {detalhe['status_aluguel']}")
            st.write(f"**Segurança Prédio/Rua (Iluminação):** {detalhe['iluminacao']}")
            st.write(f"**Fluxo Estimado de Pedestres:** {detalhe['fluxo_pessoas_dia']} hab/dia")
            
            # DIAGNÓSTICO PROFUNDO DA IA
            st.markdown("### 🧠 Parecer Ficaqui AI")
            
            if detalhe['status_aluguel'] != "Alugado":
                if detalhe['fluxo_pessoas_dia'] > 8000 and detalhe['iluminacao'] != "Boa":
                    diag = "🚨 **Alta Oportunidade Desperdiçada:** O imóvel goza de fluxo altíssimo e comercialmente viável, porém o ambiente urbano oprime a locação noturna. \n\n**Sugestões para a 'Caneta':** Acionar PPP de Iluminação. Notificar proprietários para aplicação de IPTU progressivo se retrofits não forem buscados."
                elif detalhe['status_aluguel'] == "Abandonado/IPTU Atrasado":
                    diag = "🏚️ **Déficit Total (Padrão FII):** Endividamento sobre o valor venal. Este é o alvo clássico. \n\n**Sugestão da IA:** O 'Músculo' (FII Ficaqui) deve ofertar sublocação ou desapropriação em acordo judicial. Inserir retrofit misto e dar isenção profunda para os próximos locatários âncora nos pisos térreos."
                else:
                    diag = "🏢 **Oportunidade Adormecida:** Status razoável, mas a região carece de atração orgânica pós-18h. Precisa ancorar empreendimentos que façam moradia nos pisos superiores para manter consumo local."
            else:
                if detalhe['receita_gerada'] > 150000:
                    diag = "💎 **Motor Comercial Base:** Este ativo representa um super-gerador de tributo orgânico. Deve-se maximizar a infraestrutura cruzada (calçadas e lixeiras acessíveis) pra não perder a empresa para polos periféricos."
                else:
                    diag = "✅ **Ativo Padrão:** O imóvel se sustenta. O monitoramento foca apenas em evitar que comércios vazios próximos desvalorizem este perímetro, mantendo atratividade."
            
            st.info(diag)

with tab2:
    st.subheader("Chatbot G2B: Assessor Executivo para Prefeitos/Secretários")
    st.markdown("💬 Converse de forma humanizada com seus dados base de ordenamento, isenção e urbanismo.")
    
    # Session State Chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Sou o **Ficaqui AI**. Eu cruzo dados de iluminação, fluxo de pedestres, receitas de lojistas e inadimplência do Centro. Em que rua quer focar as iniciativas de Retrofit da prefeitura hoje?"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ex: Me indique o maior problema na Rua Laranjeiras hoje.")
    
    if prompt:
        # Mostra pergunta do user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Regras Mockadas de NLP p/ resposta Ficaqui AI
        with st.chat_message("assistant"):
            prompt_lower = prompt.lower()
            
            # Condições baseadas na nova granularidade
            if "laranjeiras" in prompt_lower:
                subset = df[df['rua'] == "Rua Laranjeiras"]
                vacos = len(subset[subset['status_aluguel'] != "Alugado"])
                response = f"🔍 **Relatório Rápido da Rua Laranjeiras:**\nMapeei {len(subset)} estabelecimentos por lá. Atualmente, {vacos} estão inutilizados (seja para uso ou calote). O pior gargalo visível da métrica é a iluminação — dos abandonados, quase 80% perdem atração pois a iluminação é deficitária. Sugerimos subsidiar IPTU condicionado à iluminação de fachada (Gentileza Urbana)."
            
            elif "ilumina" in prompt_lower or "luz" in prompt_lower or "segurança" in prompt_lower:
                ruins = len(df[df['iluminacao'] == 'Ruim/Inexistente'])
                response = f"📉 **Cegueira Urbana:**\nIdentificamos que {ruins} pontos focais do Centro possuem iluminação precária. Isso tem correlação direta de 87% com a evasão nas vias comerciais após as 18h. Resolver este problema deve vir antes de isentar impostos de empresas menores, pois o risco supera a despesa."
            
            elif "receit" in prompt_lower or "arrecadação" in prompt_lower or "fundo" in prompt_lower:
                total_rec = df['receita_gerada'].sum()
                response = f"💰 **Diagnóstico Fiscal:**\nOs comerciantes saudáveis estão gerando atualmente R$ {total_rec/1e6:.1f} Milhões no Centro. No entanto, estamos perdendo mais de R$ 35 Milhões anuais nestes prédios que restam abandonados. Engatilhar as construtoras do Banese no *Fundo Músculo* para reformar e aplicar moradias no segundo andar é fundamental para injetar vida orgânica nesse setor."
            
            else:
                response = "Entendido. 🧠 Posso correlacionar esse dado e fazer uma análise de impacto financeiro, ou se preferir... Posso redigir agora mesmo a **Proposta de Projeto de Lei** baseada nesse seu pedido sobre moradia de uso misto e enviar aos gabinetes. O que acha de darmos os primeiros passos nos desertos da 'Praça Fausto Cardoso'?"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
