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

        # Resposta Via Hugging Face (InferenceClient) na verdade Groq
        with chat_container.chat_message("assistant"):
            with st.spinner("Analisando microdados com a Nuvem..."):
                try:
                    # Amostrando o DF para que caiba no contexto do limite gratuito do modelo (Zephyr 7B) // Atualizado para Llama 3.3
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
                    st.warning("Verifique se a sua chave da Groq está correta no arquivo .env ou se você atingiu o limite de requisições.")
