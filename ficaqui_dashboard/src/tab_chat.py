import streamlit as st
import pandas as pd
import os
from groq import Groq

def render_chat_tab(df: pd.DataFrame):
    st.subheader("Chatbot G2B: Inteligência Generativa sobre os Dados Urbanos")
    st.markdown("🤖 *Conectado ao Groq LLM.* Pergunte à Inteligência Artificial sobre as discrepâncias, isenções, ou como resolver os desertos mapeados.")
    
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

        # Resposta conectada com a API da Groq
        with chat_container.chat_message("assistant"):
            with st.spinner("Analisando microdados com a Nuvem..."):
                try:
                    # Amostrando o DF (Recurso do Samuel) para contexto preciso da rua
                    df_sample = df[['rua', 'status_aluguel', 'iluminacao', 'fluxo_pessoas_dia']].sample(min(15, len(df)))
                    context = df_sample.to_json(orient='records')
                     
                    # Construção do Contexto Definitivo (System Prompt)
                    system_prompt = f"""Você é o Ficaqui AI, um Assessor Executivo de GovTech & PropTech para Prefeitos e Secretários de Aracaju.
Sua missão é transformar o centro da cidade de um "cemitério imobiliário" em um hub vivo 24/7. O modelo é Asset-Light / GovTech & PropTech.

Pilar 1 (O Cérebro): AI Matchmaking. Mapeamos o caos usando dados públicos.
Pilar 2 (Vida 24/7): Uso Misto & Incentivos Inteligentes. Isenções cirúrgicas (IPTU/ISS). Térreo = âncoras comerciais, Andares superiores = retrofit residencial.
Pilar 3 (Resgate Histórico): Concessões zero-aluguel de ruínas via VR.

Aja como um urbanista sênior direto, executivo, focado em trazer clareza para a "Caneta" (Gestor Público).
Use como base exclusiva estes dados do centro da cidade (uma amostra dos imoveis): {context}."""
                    
                    # Montando o histórico limitando às 4 últimas mensagens (Recurso do Samuel)
                    messages_groq = [{"role": "system", "content": system_prompt}]
                    for m in st.session_state.messages[-4:]:
                        if m["role"] != "system":
                            messages_groq.append({"role": m["role"], "content": m["content"]})
                    
                    # Inicializa cliente Groq usando Token da Sidebar ou Env ou Secrets
                    token = st.session_state.get("groq_api_key") or os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
                    
                    if not token:
                        st.error("🔑 A chave da Groq API não foi encontrada! Por favor, insira na aba lateral (Sidebar) ou configure via dotenv.")
                        st.stop()
                        
                    client = Groq(api_key=token)
                    
                    stream = client.chat.completions.create(
                        model="llama3-70b-8192", 
                        messages=messages_groq,
                        temperature=0.7,
                        max_tokens=2048,
                        stream=True  # Efeito de Streaming (Recurso do Samuel)
                    )
                    
                    response_text = ""
                    placeholder = st.empty()
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content or ""
                        response_text += delta
                        placeholder.markdown(response_text + "▌")
                    
                    placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    st.error(f"Erro ao conectar com a IA da Groq: {e}.")
                    st.warning("💡 Verifique se inseriu a Groq API Key válida na aba lateral (⚙️ Configurações AI).")
