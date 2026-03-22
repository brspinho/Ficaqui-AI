import streamlit as st
import folium
from streamlit_folium import st_folium

def render_map_view(df):
    st.subheader("Painel de Controle Espacial")
    
    # Filtros para detalhar e cruzar
    f_status = st.multiselect("Filtrar por Status de Ocupação", df['status_aluguel'].unique(), default=df['status_aluguel'].unique())
    df_filtrado = df[df['status_aluguel'].isin(f_status)]
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        m = folium.Map(location=[-10.913, -37.052], zoom_start=15, tiles="OpenStreetMap")

        
        for i, row in df_filtrado.iterrows():
            # A cor agora determina o status de ocupação (Aluguel, Disponível, Abandonado)
            color = 'red' if row['status_aluguel'] == 'Abandonado/IPTU Atrasado' else 'orange' if row['status_aluguel'] == 'Disponível' else 'green'
            
            # O ícone determina o TIPO físico/operacional
            tipo = row['tipo']
            if tipo == 'Residencial':
                fa_icon = 'home'
            elif tipo == 'Galpão':
                fa_icon = 'industry'
            elif tipo == 'Prédio Misto':
                fa_icon = 'building'
            elif tipo == 'Sala Comercial':
                fa_icon = 'briefcase'
            else:
                fa_icon = 'shopping-cart' # Lojas Térreas / Varejo
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"<b># {row['id_espaco']}</b><br><i>{tipo}</i>",
                tooltip=f"{tipo} - Clique para analisar na Barra Lateral",
                icon=folium.Icon(color=color, icon=fa_icon, prefix='fa')
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
