"""
Script de geração do GeoJSON estático para o mapa Ficaqui.
Roda UMA VEZ. Sempre que os dados mudarem, rode novamente.

Uso:
    python scripts/generate_geojson.py
"""
import pandas as pd
import numpy as np
import json
import random

def generate_geojson():
    np.random.seed(42)
    random.seed(42)

    print("Lendo base CNEFE do Centro...")
    base_df = pd.read_csv("data/cnefe_centro_oficial.csv")

    # Jitter de ~11m para desempilhar prédios verticais
    np.random.seed(42)
    base_df['lat'] = base_df['lat'] + np.random.uniform(-0.00015, 0.00015, size=len(base_df))
    base_df['lon'] = base_df['lon'] + np.random.uniform(-0.00015, 0.00015, size=len(base_df))

    ruas_macro = {}
    features = []

    for _, row in base_df.iterrows():
        endereco = str(row['rua'])
        rua_nome = endereco.split(',')[0].strip()
        tipo_ibge = row['tipo_ibge']
        nome_estab = str(row['nome_estab'])

        # Tradução de tipologia IBGE → Ficaqui
        if tipo_ibge == "Residencial":
            tipo = "Residencial"
            status = "Alugado"
        elif tipo_ibge == "Loja/Comércio/Serviço":
            tipo = np.random.choice(["Loja Térrea", "Sala Comercial"], p=[0.7, 0.3])
            status = np.random.choice(["Alugado", "Disponível", "Abandonado/IPTU Atrasado"], p=[0.50, 0.35, 0.15])
        elif tipo_ibge == "Galpão/Ruína/Obra":
            tipo = "Galpão"
            status = np.random.choice(["Disponível", "Abandonado/IPTU Atrasado"], p=[0.3, 0.7])
        else:
            tipo = "Prédio Misto"
            status = np.random.choice(["Alugado", "Disponível", "Abandonado/IPTU Atrasado"], p=[0.6, 0.2, 0.2])

        # Dados por rua (cache interno)
        if rua_nome not in ruas_macro:
            ilum = np.random.choice(["Boa", "Regular", "Ruim/Inexistente"])
            if any(kw in rua_nome.upper() for kw in ["CALCADAO", "PRACA", "AVENIDA", "AV "]):
                flux_base = int(np.random.randint(5000, 20000))
            else:
                flux_base = int(np.random.randint(500, 10000))
            ruas_macro[rua_nome] = {"iluminacao": ilum, "fluxo": flux_base}

        iluminacao = ruas_macro[rua_nome]["iluminacao"]
        fluxo = max(0, ruas_macro[rua_nome]["fluxo"] + int(np.random.randint(-150, 150)))
        receita = int(np.random.randint(15000, 450000)) if status == "Alugado" else 0
        potencial = round(float(np.random.uniform(0.4, 0.98)), 2)

        label_id = nome_estab if nome_estab and nome_estab != 'nan' else endereco

        # Cor para a propriedade de estilo do GeoJSON
        if status == 'Abandonado/IPTU Atrasado':
            color = '#dc3545'
        elif status == 'Disponível':
            color = '#ffc107'
        else:
            color = '#28a745'

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['lon']), float(row['lat'])]  # GeoJSON é [lon, lat]!
            },
            "properties": {
                "id_espaco": label_id,
                "rua": endereco,
                "tipo": tipo,
                "status_aluguel": status,
                "iluminacao": iluminacao,
                "fluxo_pessoas_dia": fluxo,
                "receita_gerada": receita,
                "potencial_retrofit": potencial,
                "color": color
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    output_path = "data/imoveis.geojson"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    print(f"✅ GeoJSON salvo em {output_path} com {len(features)} imóveis!")
    print(f"   Tamanho: {round(len(json.dumps(geojson)) / 1024, 1)} KB")


if __name__ == "__main__":
    generate_geojson()
