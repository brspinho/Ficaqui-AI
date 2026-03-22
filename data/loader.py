import pandas as pd
import numpy as np
import requests
import streamlit as st
import random

@st.cache_data(ttl=86400) # Mantém em cache por 1 dia
def load_data():
    np.random.seed(42)  # Manter a consistência no mapa real
    random.seed(42)
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    # Limite Sul: Barão de Maruim (-10.9189). Limite Norte: Mercados (-10.9070).
    overpass_query = """
    [out:json][timeout:50];
    (
      way["building"](-10.9189,-37.0580,-10.9070,-37.0460);
      node["building"](-10.9189,-37.0580,-10.9070,-37.0460);
      node["shop"](-10.9189,-37.0580,-10.9070,-37.0460);
      way["shop"](-10.9189,-37.0580,-10.9070,-37.0460);
      node["amenity"](-10.9189,-37.0580,-10.9070,-37.0460);
      way["amenity"](-10.9189,-37.0580,-10.9070,-37.0460);
      node["office"](-10.9189,-37.0580,-10.9070,-37.0460);
      way["office"](-10.9189,-37.0580,-10.9070,-37.0460);
    );
    out center;
    """
    
    data = []
    ruas_macro_dados = {}
    
    try:
        response = requests.get(overpass_url, params={'data': overpass_query})
        response.raise_for_status()
        osm_data = response.json()
        elements = osm_data.get('elements', [])
        
        # Filtra um máximo para a visualização não travar e o LLM conseguir ler o sample depois
        if len(elements) > 2500:
            elements = random.sample(elements, 2500)
            
        for el in elements:
            tags = el.get('tags', {})
            
            # Buscando Latitude e Longitude (Ways tem center lat/lon)
            if el['type'] == 'way':
                lat = el['center']['lat']
                lon = el['center']['lon']
            else:
                lat = el['lat']
                lon = el['lon']
                
            # Identificando o Logradouro OSM
            rua_nome = tags.get('addr:street', tags.get('name', 'Centro de Aracaju'))
            # Se a rua for só "Centro de Aracaju", usamos algumas notórias do centro para mockar realismo onde o OSM falhar a tag
            if rua_nome == 'Centro de Aracaju':
                ruas_ficticias = ["Calçadão João Pessoa", "Rua São Cristóvão", "Rua Laranjeiras", "Rua Itabaiana", "Av. Rio Branco"]
                rua_nome = random.choice(ruas_ficticias)
                
            numero = tags.get('addr:housenumber', str(np.random.randint(10, 1500)))
            endereco_completo = f"{rua_nome}, {numero}"
            
            # --- Mockando informações urbanísticas sensíveis da base de dados Ficaqui ---
            status = np.random.choice(["Alugado", "Disponível", "Abandonado/IPTU Atrasado"], p=[0.45, 0.35, 0.20])
            
            osm_building_type = tags.get('building', '')
            osm_shop = tags.get('shop', '')
            osm_amenity = tags.get('amenity', '')
            osm_office = tags.get('office', '')
            
            if osm_shop or osm_amenity or osm_office or osm_building_type in ['commercial', 'retail', 'kiosk']:
                if osm_office:
                    tipo = "Sala Comercial"
                else:
                    tipo = "Loja Térrea"
            elif osm_building_type == 'warehouse':
                tipo = "Galpão"
            elif osm_building_type in ['apartments', 'residential', 'house']:
                tipo = "Residencial"
            else:
                tipo = np.random.choice(["Loja Térrea", "Galpão", "Prédio Misto", "Sala Comercial", "Residencial"])
                
            # Agrupamento macro (mesma rua compartilha fluxo e iluminação base)
            if rua_nome not in ruas_macro_dados:
                ilum = np.random.choice(["Boa", "Regular", "Ruim/Inexistente"])
                # Calçadões e grandes avenidas têm trânsito mais denso
                if "Calçadão" in rua_nome or "Praça" in rua_nome or "Avenida" in rua_nome:
                    flux_base = np.random.randint(5000, 20000)
                else:
                    flux_base = np.random.randint(500, 10000)
                ruas_macro_dados[rua_nome] = {"iluminacao": ilum, "fluxo": flux_base}
                
            iluminacao = ruas_macro_dados[rua_nome]["iluminacao"]
            # Pequeno ruído para simular variação da calçada, mas matematicamente consistente com a rua
            fluxo = ruas_macro_dados[rua_nome]["fluxo"] + np.random.randint(-150, 150)
                
            # Dados fiscais / venda
            if status == "Alugado":
                receita = np.random.randint(15000, 450000)
            else:
                receita = 0
                
            potencial = round(np.random.uniform(0.4, 0.98), 2)
            
            data.append({
                "id_espaco": f"OSM-{el['id']}",
                "rua": endereco_completo,
                "tipo": tipo,
                "lat": lat,
                "lon": lon,
                "status_aluguel": status,
                "iluminacao": iluminacao,
                "receita_gerada": receita,
                "fluxo_pessoas_dia": fluxo,
                "potencial_retrofit": potencial
            })
            
    except Exception as e:
        print(f"OSM fetch error: {e}")
        # Retorna mock simples se offline
        data.append({
            "id_espaco": "IMOVEL-OFFLINE",
            "rua": "Sistema Offline, 0", 
            "tipo": "Erro",
            "lat": -10.913,
            "lon": -37.052,
            "status_aluguel": "Alugado",
            "iluminacao": "Ruim/Inexistente",
            "receita_gerada": 0,
            "fluxo_pessoas_dia": 0,
            "potencial_retrofit": 0.0
        })

    return pd.DataFrame(data)
