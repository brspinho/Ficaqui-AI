import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data():
    np.random.seed(42)  # Manter a consistência no reload
    
    # Coordenadas reais aproximadas de ruas do Centro de Aracaju (início e fim do trecho comercial)
    vias_reais = [
        {"rua": "Calçadão João Pessoa", "lat_start": -10.9131, "lon_start": -37.0519, "lat_end": -10.9155, "lon_end": -37.0519},
        {"rua": "Praça Fausto Cardoso", "lat_start": -10.9136, "lon_start": -37.0505, "lat_end": -10.9140, "lon_end": -37.0500},
        {"rua": "Rua Laranjeiras", "lat_start": -10.9125, "lon_start": -37.0525, "lat_end": -10.9125, "lon_end": -37.0560},
        {"rua": "Rua Itabaiana", "lat_start": -10.9121, "lon_start": -37.0540, "lat_end": -10.9160, "lon_end": -37.0540},
        {"rua": "Rua Geru", "lat_start": -10.9142, "lon_start": -37.0516, "lat_end": -10.9142, "lon_end": -37.0545},
        {"rua": "Rua São Cristóvão", "lat_start": -10.9138, "lon_start": -37.0528, "lat_end": -10.9138, "lon_end": -37.0565},
        {"rua": "Avenida Rio Branco", "lat_start": -10.9135, "lon_start": -37.0495, "lat_end": -10.9180, "lon_end": -37.0495},
        {"rua": "Rua Capela", "lat_start": -10.9150, "lon_start": -37.0522, "lat_end": -10.9150, "lon_end": -37.0555},
        {"rua": "Rua Propriá", "lat_start": -10.9165, "lon_start": -37.0530, "lat_end": -10.9165, "lon_end": -37.0570},
        {"rua": "Rua Santo Amaro", "lat_start": -10.9170, "lon_start": -37.0525, "lat_end": -10.9170, "lon_end": -37.0560},
        {"rua": "Praça General Valadão", "lat_start": -10.9118, "lon_start": -37.0510, "lat_end": -10.9122, "lon_end": -37.0515},
        {"rua": "Avenida Barão de Maruim", "lat_start": -10.9189, "lon_start": -37.0520, "lat_end": -10.9189, "lon_end": -37.0580}
    ]
    
    data = []
    
    # Gerando imóveis ao longo do segmento de reta de cada rua
    for i, via in enumerate(vias_reais):
        num_imoveis = np.random.randint(6, 18)  # Quantidade de imóveis por rua
        rua_nome = via["rua"]
        
        for j in range(num_imoveis):
            # Interpolação linear para posicionar o imóvel ao longo da rua
            t = j / max(1, (num_imoveis - 1))
            
            # Adicionando um pequeníssimo ruído para simular os dois lados da rua (imóveis não ficam perfeitamente no centro)
            jitter_lat = np.random.uniform(-0.00015, 0.00015)
            jitter_lon = np.random.uniform(-0.00015, 0.00015)
            
            lat = via["lat_start"] + t * (via["lat_end"] - via["lat_start"]) + jitter_lat
            lon = via["lon_start"] + t * (via["lon_end"] - via["lon_start"]) + jitter_lon
            
            # Gerando numeração predial realista
            numero_imovel = np.random.randint(10, 1500)
            endereco_completo = f"{rua_nome}, {numero_imovel}"
            
            # Mockando características reais do imóvel
            status = np.random.choice(["Alugado", "Disponível", "Abandonado/IPTU Atrasado"], p=[0.45, 0.35, 0.20])
            tipo = np.random.choice(["Loja Térrea", "Galpão", "Prédio Misto", "Sala Comercial"])
            iluminacao = np.random.choice(["Boa", "Regular", "Ruim/Inexistente"])
            
            # Ajustando fluxo baseado na rua (Calçadões têm mais fluxo)
            if "Calçadão" in rua_nome or "Praça" in rua_nome:
                fluxo = np.random.randint(5000, 20000)
            else:
                fluxo = np.random.randint(500, 10000)
            
            # Imóveis alugados geram receita alta. Disponíveis podem zerar e os abandonados devem impostos
            if status == "Alugado":
                receita = np.random.randint(15000, 450000)
            else:
                receita = 0
                
            potencial = round(np.random.uniform(0.4, 0.98), 2)
            
            data.append({
                "id_espaco": f"IMOVEL-{str(i).zfill(2)}-{str(j).zfill(2)}",
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
            
    return pd.DataFrame(data)
