import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

def render_map_view(df):
    st.subheader("Painel de Controle Espacial")
    
    # Filtros para detalhar e cruzar
    f_status = st.multiselect("Filtrar por Status de Ocupação", df['status_aluguel'].unique(), default=df['status_aluguel'].unique())
    df_filtrado = df[df['status_aluguel'].isin(f_status)]

    # A trava de segurança de 1000 itens da branch de testes foi removida.
    # Graças às otimizações de SVG Circle e Jitter Math, o Front-end flui com 100% (6330+) pontos originais.
    df_mapa = df_filtrado
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        m = folium.Map(location=[-10.913, -37.052], zoom_start=15, tiles="OpenStreetMap")
        
        # MarkerCluster agora "explode" e revela os pinos individuais nas ruas originais a partir do Zoom 16!
        # maxClusterRadius diminui a "gravidade" do cluster, separando-os mais cedo.
        marker_cluster = MarkerCluster(
            options={
                'disableClusteringAtZoom': 16,
                'maxClusterRadius': 35
            }
        ).add_to(m)
        
        for i, row in df_mapa.iterrows():
            # A cor agora determina o status de ocupação (Aluguel, Disponível, Abandonado)
            color = 'red' if row['status_aluguel'] == 'Abandonado/IPTU Atrasado' else 'orange' if row['status_aluguel'] == 'Disponível' else 'green'
            
            tipo = row['tipo']
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=5, # Tamanho muito menor e focado na performance
                color=color, # Bordas
                weight=1,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=f"<b>{row['id_espaco']}</b><br><i>{tipo}</i>",
                tooltip=f"{tipo} - Clique para analisar na Barra Lateral"
            ).add_to(marker_cluster) # Adicionado ao Cluster em vez do mapa Base!
            
        # O st_folium captura eventos de clique no web app limitando o retorno para não recarregar no pan/zoom
        st_data = st_folium(
            m, 
            use_container_width=True, 
            height=550, 
            key="main_ficaqui_map",
            returned_objects=["last_object_clicked"]
        )
        
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
