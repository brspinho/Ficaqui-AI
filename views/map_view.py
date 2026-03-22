import streamlit as st
import pydeck as pdk
import pandas as pd

def render_map_view(df, planning_params):
    st.subheader("Inteligência de Planejamento Espacial")
    
    # Extrai parâmetros do sidebar
    meta = planning_params.get("ocupacao_meta", 85)
    retrofit_ativo = planning_params.get("retrofit_mode", True)
    
    # Filtros de visualização rápidos (compactos)
    f_status = st.multiselect(
        "Status de Exibição", 
        df['status_aluguel'].unique(), 
        default=df['status_aluguel'].unique()
    )
    df_filtrado = df[df['status_aluguel'].isin(f_status)]
    
    # Cálculo de métricas de planejamento
    ocupados = len(df_filtrado[df_filtrado['status_aluguel'] == 'Alugado'])
    total = len(df_filtrado) if len(df_filtrado) > 0 else 1
    ocupacao_atual = (ocupados / total) * 100
    dif = ocupacao_atual - meta
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Taxa de Ocupação Atual", f"{ocupacao_atual:.1f}%", delta=f"{dif:.1f}% vs Meta")
    m2.metric("Meta de Governo", f"{meta}%")
    m3.metric("Imóveis p/ Retrofit", len(df_filtrado[df_filtrado['status_aluguel'] == 'Abandonado/IPTU Atrasado']))
    
    st.markdown("---")

    # Mapeamento de cores para status
    # Color format: [R, G, B, Alpha]
    df_temp = df_filtrado.copy()
    df_temp['color'] = df_temp['status_aluguel'].apply(
        lambda x: [255, 0, 0, 200] if x == 'Abandonado/IPTU Atrasado' 
        else [255, 165, 0, 200] if x == 'Disponível' 
        else [0, 255, 0, 200]
    )
    
    # Tamanho do marcador (Destaque para Retrofit se ativo)
    df_temp['radius'] = df_temp['status_aluguel'].apply(
        lambda x: 15 if (retrofit_ativo and x == 'Abandonado/IPTU Atrasado') else 8
    )

    # Camada do Mapa (Pydeck para Performance)
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_temp,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="radius",
        pickable=True,
        opacity=0.8,
        stroked=True,
        get_line_color=[255, 255, 255],
        get_line_width=1,
    )

    view_state = pdk.ViewState(
        latitude=-10.913,
        longitude=-37.052,
        zoom=14,
        pitch=0
    )

    c1, c2 = st.columns([2, 1])
    
    with c1:
        # Renderização do Mapa
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/light-v9",
            tooltip={
                "html": "<b>Status:</b> {status_aluguel}<br/><b>Tipo:</b> {tipo}<br/><b>Rua:</b> {rua}",
                "style": {"color": "white"}
            }
        )
        st.pydeck_chart(r)
        
    with c2:
        st.subheader("Diagnóstico do Espaço")
        
        # SelectBox para filtrar imóveis específicos (Top 500 do filtro para não travar o seletor)
        espaco_selecionado = st.selectbox(
            "Analisar Imóvel:", 
            df_filtrado['id_espaco'].head(500)
        )
        
        if espaco_selecionado:
            detalhe = df_filtrado[df_filtrado['id_espaco'] == espaco_selecionado].iloc[0]
            st.write(f"**Logradouro:** {detalhe['rua']}")
            st.write(f"**Tipologia Principal:** {detalhe['tipo']}")
            st.write(f"**Status de Aluguel:** {detalhe['status_aluguel']}")
            st.write(f"**Infra. de Iluminação:** {detalhe['iluminacao']}")
            st.write(f"**Fluxo Diário Estimado:** {detalhe['fluxo_pessoas_dia']} hab/dia")
            
            # DIAGNÓSTICO PROFUNDO DA IA
            st.markdown("### Overview Rápido")
            
            if detalhe['status_aluguel'] != "Alugado":
                if detalhe['fluxo_pessoas_dia'] > 8000 and detalhe['iluminacao'] != "Boa":
                    diag = "Fluxo altíssimo e comercialmente viável, porém o ambiente urbano oprime a locação noturna. Ação: Notificar proprietários para IPTU progressivo ou iluminar entorno."
                elif detalhe['status_aluguel'] == 'Abandonado/IPTU Atrasado':
                    diag = "Endividamento sobre o valor venal. O Fundo Imobiliário (FII Ficaqui) deve focar na desapropriação e aplicar retrofit misto (Loja Embaixo + Moradia Em Cima)."
                else:
                    diag = "Oportunidade Subutilizada. Falta atração orgânica pós-18h. Precisa ancorar empreendimentos mistos."
            else:
                if detalhe['receita_gerada'] > 150000:
                    diag = "Motor Comercial Forte! Manter calçadas e segurança em dia para não perder este lojista para shoppings fechados."
                else:
                    diag = "✅ Ativo locado e operante. Exige apenas manutenção básica da prefeitura."
            
            st.info(diag)
