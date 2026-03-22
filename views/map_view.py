import json
import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium

GEOJSON_PATH = "data/imoveis.geojson"


@st.cache_data
def _load_geojson_filtered(status_filter: tuple) -> dict:
    """GeoJSON filtrado por status — carregado e filtrado UMA VEZ, em cache RAM."""
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        all_features = json.load(f)["features"]
    features = [f for f in all_features if f["properties"]["status_aluguel"] in status_filter]
    return {"type": "FeatureCollection", "features": features}


def render_map_view(df):
    st.subheader("Painel de Controle Espacial")

    f_status = st.multiselect(
        "Filtrar por Status de Ocupação",
        df["status_aluguel"].unique(),
        default=df["status_aluguel"].unique()
    )

    c1, c2 = st.columns([2, 1])

    with c1:
        geojson = _load_geojson_filtered(tuple(sorted(f_status)))

        m = folium.Map(location=[-10.913, -37.052], zoom_start=15, tiles="OpenStreetMap")

        # folium.GeoJson envia UM ÚNICO payload JSON ao browser (vs 6330 objetos Python).
        # O Leaflet renderiza os círculos coloridos nativamente em JavaScript.
        # fill=True no template + fillColor no style_function garante o preenchimento.
        folium.GeoJson(
            geojson,
            marker=folium.CircleMarker(
                radius=5,
                fill=True,              # CRITICO: garante preenchimento
                fill_opacity=0.85,
                weight=1.2,
            ),
            style_function=lambda feature: {
                "fillColor": feature["properties"]["color"],
                "color": feature["properties"]["color"],
                "fillOpacity": 0.85,
                "weight": 1.2,
            },
            highlight_function=lambda _: {
                "fillOpacity": 1.0,
                "weight": 3,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["tipo", "status_aluguel"],
                aliases=["Tipo:", "Status:"],
                style="font-size:13px",
                sticky=True,
            ),
        ).add_to(m)

        st_data = st_folium(
            m,
            use_container_width=True,
            height=550,
            key="ficaqui_map_" + "_".join(sorted(f_status)),
            returned_objects=["last_object_clicked"],
        )

    with c2:
        st.subheader("🏢 Diagnóstico do Espaço")

        # Clique: encontrar imóvel mais próximo no df
        clicked = st_data.get("last_object_clicked") if st_data else None
        if clicked and clicked.get("lat"):
            lat_c, lon_c = clicked["lat"], clicked["lng"]
            df_filt = df[df["status_aluguel"].isin(f_status)]
            dist = (df_filt["lat"] - lat_c) ** 2 + (df_filt["lon"] - lon_c) ** 2
            st.session_state["clicked_espaco"] = df_filt.loc[dist.idxmin()]["id_espaco"]

        espaco_inicial = st.session_state.get("clicked_espaco", df["id_espaco"].iloc[0])
        try:
            default_idx = int(df.index[df["id_espaco"] == espaco_inicial][0])
        except (IndexError, KeyError):
            default_idx = 0

        espaco_selecionado = st.selectbox(
            "📍 Selecione ou clique no mapa:",
            df["id_espaco"],
            index=default_idx,
        )

        if espaco_selecionado:
            detalhe = df[df["id_espaco"] == espaco_selecionado].iloc[0]
            st.write(f"**Logradouro:** {detalhe['rua']}")
            st.write(f"**Tipologia:** {detalhe['tipo']}")
            st.write(f"**Status:** {detalhe['status_aluguel']}")
            st.write(f"**Iluminação:** {detalhe['iluminacao']}")
            st.write(f"**Fluxo Diário:** {int(detalhe['fluxo_pessoas_dia']):,} hab/dia")

            st.markdown("### 📊 Overview Rápido")
            s = detalhe["status_aluguel"]
            fl = detalhe["fluxo_pessoas_dia"]
            il = detalhe["iluminacao"]
            re = detalhe["receita_gerada"]

            if s != "Alugado":
                if fl > 8000 and il != "Boa":
                    diag = "🚨 Fluxo altíssimo mas iluminação oprime locação noturna. Ação: IPTU progressivo ou iluminar entorno."
                elif s == "Abandonado/IPTU Atrasado":
                    diag = "🏚️ Endividamento sobre valor venal. FII Ficaqui deve atuar com retrofit misto (comércio + moradia)."
                else:
                    diag = "🏢 Oportunidade subutilizada. Precisa de âncoras e atração orgânica pós-18h."
            else:
                diag = "💎 Motor Comercial Forte!" if re > 150000 else "✅ Ativo locado e operante. Exige apenas manutenção básica."

            st.info(diag)
