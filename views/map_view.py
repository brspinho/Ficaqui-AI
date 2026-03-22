import json
import numpy as np
import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import HeatMap, FastMarkerCluster

GEOJSON_PATH = "data/imoveis.geojson"

# JavaScript callback para o FastMarkerCluster: desenha círculos coloridos
# Cada row = [lat, lon, color, tooltip_html]
_CLUSTER_CALLBACK = """
function(row) {
    var marker = L.circleMarker(
        new L.LatLng(row[0], row[1]),
        {
            radius: 6,
            color: row[2],
            weight: 1.2,
            fillColor: row[2],
            fillOpacity: 0.85
        }
    );
    marker.bindTooltip(row[3], {sticky: true});
    return marker;
}
"""


@st.cache_data
def _load_geojson_filtered(status_filter: tuple) -> dict:
    """Carrega o GeoJSON pré-calculado e retém apenas os status selecionados."""
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        all_features = json.load(f)["features"]
    features = [f for f in all_features if f["properties"]["status_aluguel"] in status_filter]
    return {"type": "FeatureCollection", "features": features}


@st.cache_data
def _get_cluster_data(status_filter: tuple) -> list:
    """Prepara os dados no formato [lat, lon, color, tooltip] para o FastMarkerCluster."""
    icons = {"Residencial": "🏠", "Galpão": "🏭", "Prédio Misto": "🏢", "Sala Comercial": "💼"}
    geojson = _load_geojson_filtered(status_filter)
    rows = []
    for feat in geojson["features"]:
        props = feat["properties"]
        lon, lat = feat["geometry"]["coordinates"]
        tipo = props["tipo"]
        icon = icons.get(tipo, "🛒")
        tip = f"{icon} <b>{tipo}</b><br/>Status: {props['status_aluguel']}"
        rows.append([lat, lon, props["color"], tip])
    return rows


def _build_heatmap_data(status_filter: tuple, metrica: str) -> list:
    """Extrai coordenadas e pesos para a camada de calor."""
    geojson = _load_geojson_filtered(status_filter)
    heat_data = []
    for f in geojson["features"]:
        props = f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        weight = 0.0
        if metrica == "🔥 Fluxo de Pessoas":
            weight = float(props.get("fluxo_pessoas_dia", 0)) / 20000.0
        elif metrica == "💰 Oportunidade/Potencial":
            if props.get("status_aluguel") != "Alugado":
                weight = float(props.get("potencial_retrofit", 0))
            else:
                weight = float(props.get("receita_gerada", 0)) / 500000.0
        elif metrica == "🌑 Zonas Escuras (Risco)":
            ilu = props.get("iluminacao", "")
            if ilu == "Ruim/Inexistente": weight = 1.0
            elif ilu == "Regular": weight = 0.4
        if weight > 0:
            heat_data.append([lat, lon, weight])
    return heat_data


def generate_time_series(tipo_imovel: str, fluxo_total: int) -> pd.DataFrame:
    """Cria uma curva sino preditiva (Bell Curve) das 00h às 23h."""
    horas = list(range(24))
    pesos = np.zeros(24)
    if tipo_imovel in ["Loja Térrea", "Sala Comercial"]:
        for h in horas:
            if 8 <= h <= 18:
                pesos[h] = np.exp(-0.5 * ((h - 13) / 2.5) ** 2)
    elif tipo_imovel == "Galpão":
        for h in horas:
            if 6 <= h <= 18:
                pesos[h] = np.exp(-0.5 * ((h - 8) / 1.5) ** 2) + np.exp(-0.5 * ((h - 17) / 1.5) ** 2)
    else:  # Residencial / Misto
        for h in horas:
            pesos[h] = np.exp(-0.5 * ((h - 7) / 2.0) ** 2) + np.exp(-0.5 * ((h - 19) / 2.5) ** 2) + 0.1
    pesos = pesos / np.sum(pesos)
    fluxo_hora = [int(p * fluxo_total) for p in pesos]
    df_ts = pd.DataFrame({"Hora": [f"{h:02d}h" for h in horas], "Pedestres": fluxo_hora})
    return df_ts.set_index("Hora")


def render_map_view(df):
    st.subheader("Painel de Controle Espacial")

    f_status = st.multiselect(
        "Filtrar por Status de Ocupação",
        df["status_aluguel"].unique(),
        default=df["status_aluguel"].unique()
    )

    modo_visao = st.radio(
        "Lente Espacial:",
        ["📍 Visão Micro (Lotes/Imóveis)", "🌡️ Visão Macro (Mapas de Calor)"],
        horizontal=True
    )

    metrica_calor = None
    if modo_visao == "🌡️ Visão Macro (Mapas de Calor)":
        metrica_calor = st.selectbox(
            "Camada Termográfica:",
            ["🔥 Fluxo de Pessoas", "💰 Oportunidade/Potencial", "🌑 Zonas Escuras (Risco)"]
        )

    c1, c2 = st.columns([2, 1])
    status_tuple = tuple(sorted(f_status))

    with c1:
        # Sempre usar OpenStreetMap (claro) para boa legibilidade do heatmap e dos pontos
        m = folium.Map(location=[-10.913, -37.052], zoom_start=15, tiles="OpenStreetMap")

        if modo_visao == "📍 Visão Micro (Lotes/Imóveis)":
            # FastMarkerCluster: clustering via JS sem loop Python, círculos coloridos via callback
            cluster_data = _get_cluster_data(status_tuple)
            FastMarkerCluster(
                data=cluster_data,
                callback=_CLUSTER_CALLBACK,
                options={"disableClusteringAtZoom": 17, "maxClusterRadius": 40}
            ).add_to(m)
        else:
            # HeatMap com gradiente vibrante sobre mapa claro
            heat_data = _build_heatmap_data(status_tuple, metrica_calor)
            gradients = {
                "🔥 Fluxo de Pessoas":    {0.2: "#ffffb2", 0.5: "#fd8d3c", 0.8: "#f03b20", 1.0: "#bd0026"},
                "💰 Oportunidade/Potencial": {0.2: "#edf8b1", 0.5: "#7fcdbb", 0.8: "#2c7fb8", 1.0: "#253494"},
                "🌑 Zonas Escuras (Risco)": {0.3: "#fee5d9", 0.6: "#fc9272", 0.85: "#de2d26", 1.0: "#67000d"},
            }
            gradient = gradients.get(metrica_calor, {0.4: "lime", 0.7: "orange", 1.0: "red"})
            HeatMap(heat_data, radius=20, blur=18, min_opacity=0.4, gradient=gradient).add_to(m)

        map_key = f"ficaqui_map_{'_'.join(sorted(f_status))}_{modo_visao}_{metrica_calor}"
        st_data = st_folium(m, use_container_width=True, height=650, key=map_key, returned_objects=["last_object_clicked"])

    with c2:
        st.subheader("🏢 Diagnóstico do Espaço")

        clicked = st_data.get("last_object_clicked") if st_data else None
        if clicked and clicked.get("lat"):
            lat_c, lon_c = clicked["lat"], clicked["lng"]
            df_filt = df[df["status_aluguel"].isin(f_status)]
            if not df_filt.empty:
                dist = (df_filt["lat"] - lat_c) ** 2 + (df_filt["lon"] - lon_c) ** 2
                st.session_state["clicked_espaco"] = df_filt.loc[dist.idxmin()]["id_espaco"]

        espaco_inicial = st.session_state.get("clicked_espaco", df["id_espaco"].iloc[0])
        try:
            default_idx = int(df.index[df["id_espaco"] == espaco_inicial][0])
        except (IndexError, KeyError):
            default_idx = 0

        espaco_selecionado = st.selectbox("📍 Selecione ou clique no lote:", df["id_espaco"], index=default_idx)

        if espaco_selecionado:
            detalhe = df[df["id_espaco"] == espaco_selecionado].iloc[0]
            st.write(f"**Tipologia:** {detalhe['tipo']}")
            st.write(f"**Status:** {detalhe['status_aluguel']}")
            st.write(f"**Iluminação Base:** {detalhe['iluminacao']}")
            st.write(f"**VPT (Volume Pedonal Total):** {int(detalhe['fluxo_pessoas_dia']):,} hab/dia")

            st.markdown("### 📈 Fluxo Preditivo Diário")
            df_temporal = generate_time_series(detalhe["tipo"], detalhe["fluxo_pessoas_dia"])
            st.area_chart(df_temporal, color="#ECA118")

            st.markdown("### 📊 Inteligência Ficaqui")
            s = detalhe["status_aluguel"]
            fl = detalhe["fluxo_pessoas_dia"]
            il = detalhe["iluminacao"]
            re = detalhe["receita_gerada"]

            if s != "Alugado":
                if fl > 8000 and il != "Boa":
                    diag = "🚨 **Bloqueio Inconsciente:** Alto fluxo diurno colide com arquitetura noturna hostil. Recomenda-se IPTU progressivo ou revitalização do entorno."
                elif s == "Abandonado/IPTU Atrasado":
                    diag = "🏚️ **Passivo Ativado:** FII Ficaqui deve visar aquisição e aplicar retrofit *Multiuso* (Vitrine Comercial + Moradia)."
                else:
                    diag = "🏢 **Oportunidade Adormecida:** Necessita âncoras locais de cultura ou gastronomia para tração pós-18h."
            else:
                diag = "💎 **Core Asset Comercial!** Manter iluminação e infraestrutura para evitar migração do lojista." if re > 150000 else "✅ Ativo perfeitamente locado e operante."

            st.success(diag)
