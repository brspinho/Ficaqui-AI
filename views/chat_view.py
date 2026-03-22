import streamlit as st
from groq import Groq

def render_chat_view(df, groq_key=None):
    if not groq_key:
        import os
        groq_key = os.getenv("GROQ_API_KEY")
    st.subheader("Chatbot G2B: Inteligência Generativa sobre os Dados Urbanos")
    st.markdown("*Conectado ao Agente Urbano.* Pergunte à Inteligência Artificial sobre as discrepâncias, isenções, ou como resolver os desertos mapeados.")
    
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

        # Resposta Via Groq
        with chat_container.chat_message("assistant"):
            with st.spinner("Analisando microdados com a Nuvem..."):
                try:
                    # Carrega os prédios públicos estratégicos (Novo CSV)
                    import pandas as pd
                    try:
                        df_predios = pd.read_csv("data/Prdio-Localizao-Natureza-Situaodescritanasfontes-Porquefortecandidatoahubtechusomisto.csv")
                        predios_context = df_predios.to_json(orient='records')
                    except:
                        predios_context = "[]"

                    # Amostrando o DF CNEFE para que caiba no contexto do limite do modelo
                    df_sample = df[['rua', 'status_aluguel', 'iluminacao', 'fluxo_pessoas_dia', 'crimes_mes', 'cobertura_policial', 'indice_seguranca', 'incentivo_icms']].sample(min(15, len(df)))
                    context = df_sample.to_json(orient='records')
                    
                    system_prompt = f"""Você é o Ficaqui AI, um Urbanista Sênior de Aracaju/Brasil orientando o Governo do Estado de Sergipe e Fundos de Investimentos (FII).

Sua missão é dar respostas EXTENSAS, ANALÍTICAS e RICAS EM DADOS. Evite respostas curtas de um parágrafo.

REGRAS OBRIGATÓRIAS:
1. FOCO ESTADUAL E FEDERAL: Ignore o IPTU. Foque em ICMS (Estado), Fundos PPP, Retrofits de Investimento e destinação de patrimônios públicos.
2. CRUZAMENTO OBRIGATÓRIO (DOUBLE EVIDENCE): Sempre que sugerir algo para um Prédio Público (ex: Hotel Palace), você DEVE cruzar com os dados das ruas ao redor (Microdados CNEFE). Diga: "Instalar um Hub no Hotel Palace é ideal porque as ruas X e Y têm fluxo de N pessoas e índice de segurança K...". Prove sua tese misturando os DOIS datasets fornecidos.
3. IDIOMA: Responda apenas em Português do Brasil impecável.
4. LÓGICA URBANÍSTICA:
 - Prédios Estaduais (Hotel Palace) -> prioridade de Hubs Tech/Moradia via incentivos de ICMS para atrair empresas do polo de tecnologia.
 - Relação Luz x Crime -> Ruas escuras ou abandonadas geram crimes. Instalar um Hub com comércio 24h em um Prédio Público adjacente resolve o ecossistema.
 - INCENTIVOS INVERSOS: O bônus de "Crédito ICMS" é inversamente proporcional à valorização da rua. Quanto MENOS fluxo, PIOR a iluminação e mais ocioso for o imóvel, MAIOR deve ser o valor de crédito sugerido para incentivar o empreendedor a desbravar a revitalização do pior cenário.
 - Use os números exatos (ex: {df_sample.iloc[0]['rua'] if not df_sample.empty else 'Rua Exemplo'} tem tantos crimes/mês) para validar.

Microdados CNEFE (Amostra de Vizinhança): {context}

Prédios Públicos Estratégicos para Revitalização: {predios_context}"""

                    messages_hf = [{"role": "system", "content": system_prompt}]
                    for m in st.session_state.messages[-4:]:  # last 4
                        if m["role"] != "system":
                            messages_hf.append({"role": m["role"], "content": m["content"]})
                    
                    # Conectar a Groq
                    if not groq_key:
                        st.error("Por favor, preencha sua GROQ_API_KEY no arquivo .env ou na aba lateral.")
                        st.stop()
                        
                    client = Groq(api_key=groq_key)
                    
                    # Stream the real AI response usando Groq API
                    response = ""
                    stream = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
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
                            placeholder.markdown(response + "|")
                    placeholder.markdown(response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"Erro ao contatar API da Groq. Detalhes: {e}")
                    st.warning("Verifique se a sua chave da Groq está correta no arquivo .env ou se você atingiu o limite de requisições.")
