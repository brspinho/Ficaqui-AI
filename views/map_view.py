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


# Gradiente universal Verde → Amarelo → Vermelho
_VERDE_VERMELHO = {0.0: "#00c800", 0.4: "#ffff00", 0.7: "#ff8c00", 1.0: "#cc0000"}


def _build_heatmap_data(status_filter: tuple, metrica: str) -> list:
    """Extrai coordenadas e pesos [0-1] normalizados para o HeatMap."""
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
        elif metrica == "💡 Iluminação Noturna (Risco)":
            ilu = props.get("iluminacao", "")
            # Verde = boa iluminação, Vermelho = sem iluminação
            weight = {"Ruim/Inexistente": 1.0, "Regular": 0.45, "Boa": 0.1}.get(ilu, 0)
        elif metrica == "🚨 Crimes por Mês":
            crimes = float(props.get("crimes_mes", 0))
            weight = min(1.0, crimes / 20.0)  # Normalizado pelo teto de 20 crimes/mês
        elif metrica == "👮 Cobertura Policial":
            # Verde = alta cobertura, Vermelho = baixa cobertura (escala invertida)
            weight = 1.0 - float(props.get("cobertura_policial", 0.5))
        elif metrica == "🛡️ Índice de Segurança":
            # Verde = seguro, Vermelho = inseguro (escala invertida: 10=verde, 0=vermelho)
            weight = 1.0 - float(props.get("indice_seguranca", 5)) / 10.0

        if weight > 0.01:
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


def generate_police_timeseries(cobertura_base: float, iluminacao: str) -> pd.DataFrame:
    """Curva de presença policial ao longo do dia.
    - Pico em horário comercial (08h-18h) e virada da noite (22h-01h)
    - Zona escura penaliza presença noturna
    """
    horas = list(range(24))
    pesos = np.zeros(24)
    for h in horas:
        # Turno diurno: policiamento ostensivo
        pesos[h] += cobertura_base * np.exp(-0.5 * ((h - 10) / 3.5) ** 2)
        # Turno noturno: patrulhamento preventivo
        noturno = cobertura_base * np.exp(-0.5 * ((h - 23) / 2.0) ** 2)
        if iluminacao == "Ruim/Inexistente":
            noturno *= 0.4  # Rua escura: polícia evita
        elif iluminacao == "Regular":
            noturno *= 0.7
        pesos[h] += noturno
    max_p = max(pesos) if max(pesos) > 0 else 1
    presenca = [round(p / max_p * cobertura_base * 100, 1) for p in pesos]
    df = pd.DataFrame({"Hora": [f"{h:02d}h" for h in horas], "Presença (%)" : presenca})
    return df.set_index("Hora")


def generate_crime_breakdown(crimes_mes: int, iluminacao: str, status: str) -> pd.DataFrame:
    """Distribuição ficticia de crimes por tipo e período, baseada no perfil do imóvel."""
    # Crimes tendem a ser mais noturnos em zonas escuras / abandonadas
    fator_noite = {"Ruim/Inexistente": 0.70, "Regular": 0.55, "Boa": 0.35}.get(iluminacao, 0.5)
    fator_abandono = 1.5 if status == "Abandonado/IPTU Atrasado" else 1.0

    diurno = int(crimes_mes * (1 - fator_noite))
    noturno = int(crimes_mes * fator_noite)

    # Distribui crimes por tipo (proporcional ao total)
    tipos = {
        "Furto/Roubo": int(crimes_mes * 0.45 * fator_abandono),
        "Uso de Drogas": int(crimes_mes * 0.25),
        "Vandalismo": int(crimes_mes * 0.15),
        "Agressão": int(crimes_mes * 0.10),
        "Outros": int(crimes_mes * 0.05),
    }
    df = pd.DataFrame.from_dict(
        tipos, orient="index", columns=["Ocorrências/mês"]
    )
    df.index.name = "Tipo de Crime"
    return df, diurno, noturno


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
            [
                "🔥 Fluxo de Pessoas",
                "💰 Oportunidade/Potencial",
                "💡 Iluminação Noturna (Risco)",
                "🚨 Crimes por Mês",
                "👮 Cobertura Policial",
                "🛡️ Índice de Segurança",
            ]
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
            # HeatMap: sempre verde→amarelo→vermelho para leitura intuitiva universal
            heat_data = _build_heatmap_data(status_tuple, metrica_calor)
            HeatMap(heat_data, radius=22, blur=18, min_opacity=0.45, gradient=_VERDE_VERMELHO).add_to(m)

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

            # Métricas de Segurança Pública
            with st.expander("🛡️ Segurança Pública", expanded=False):
                crimes_mes = int(detalhe.get('crimes_mes', 0))
                cobertura = float(detalhe.get('cobertura_policial', 0.5))
                idx_seg = float(detalhe.get('indice_seguranca', 5))
                ilum = detalhe['iluminacao']
                cor_seg = "🟢" if idx_seg >= 7 else "🟡" if idx_seg >= 4 else "🔴"

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("🚨 Crimes/mês", crimes_mes)
                col_b.metric("👮 Policiamento", f"{int(cobertura * 100)}%")
                col_c.metric("🛡️ Segurança", f"{idx_seg}/10", delta=cor_seg)

                st.caption("🕒 **Presença Policial por Hora (Estimada)**")
                df_pol = generate_police_timeseries(cobertura, ilum)
                st.area_chart(df_pol, color="#1E88E5")

                df_crimes, diurno, noturno = generate_crime_breakdown(crimes_mes, ilum, detalhe['status_aluguel'])
                st.caption(f"🌞 Diurno: **{diurno}** | 🌙 Noturno: **{noturno}** ocorrências/mês")
                st.bar_chart(df_crimes, color="#E53935")

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
