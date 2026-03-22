import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data():
    np.random.seed(42)  # Para consistencia reload
    ruas = [
        "Calçadão João Pessoa", "Rua Itabaiana", "Rua Laranjeiras", "Rua Geru", "Praça Fausto Cardoso",
        "Rua São Cristóvão", "Rua Apodi", "Avenida Rio Branco", "Rua Capela", "Travessa José de Faro",
        "Rua Propriá", "Rua Santo Amaro", "Rua Japaratuba", "Praça General Valadão", "Avenida Barão de Maruim"
    ]
    lat_base, lon_base = -10.913, -37.052
    
    data = []
    # Gerando múltiplos imóveis por rua (granularidade alta)
    for i, rua in enumerate(ruas):
        num_imoveis = np.random.randint(4, 12)
        for j in range(num_imoveis):
            lat = lat_base + np.random.uniform(-0.008, 0.008)
            lon = lon_base + np.random.uniform(-0.008, 0.008)
            status = np.random.choice(["Alugado", "Disponível", "Abandonado/IPTU Atrasado"], p=[0.4, 0.3, 0.3])
            tipo = np.random.choice(["Loja Térrea", "Galpão", "Prédio Misto", "Sala Comercial"])
            iluminacao = np.random.choice(["Boa", "Regular", "Ruim/Inexistente"])
            fluxo = np.random.randint(500, 15000)
            
            # Imóveis alugados geram receita alta. Disponíveis podem zerar e os abandonados devem impostos
            if status == "Alugado":
                receita = np.random.randint(10000, 350000)
            else:
                receita = 0
                
            potencial = round(np.random.uniform(0.3, 0.95), 2)
            
            data.append({
                "id_espaco": f"IMOVEL-{str(i).zfill(2)}-{str(j).zfill(2)}",
                "rua": rua,
                "tipo": tipo,
                "lat": lat,
                "lon": lon,
                "status_aluguel": status,
                "iluminacao": iluminacao,
                "receita_gerada": receita,
                "fluxo_pessoas_dia": fluxo,
                "potencial_retrofit": potencial
            })
            
    return pd.DataFrame(data)
