import pandas as pd
import numpy as np

def generate_cnefe_mock_csv():
    np.random.seed(42)
    
    # Ruas reais do Centro de Aracaju com suas coordenadas de início e fim.
    # Expandido para cobrir toda a região solicitada (até a Barão de Maruim).
    vias_reais = [
        {"rua": "Calçadão João Pessoa", "lat_start": -10.9100, "lon_start": -37.0519, "lat_end": -10.9155, "lon_end": -37.0519},
        {"rua": "Praça Fausto Cardoso", "lat_start": -10.9136, "lon_start": -37.0505, "lat_end": -10.9140, "lon_end": -37.0500},
        {"rua": "Rua Laranjeiras", "lat_start": -10.9125, "lon_start": -37.0490, "lat_end": -10.9125, "lon_end": -37.0560},
        {"rua": "Rua Itabaiana", "lat_start": -10.9110, "lon_start": -37.0540, "lat_end": -10.9189, "lon_end": -37.0540},
        {"rua": "Rua Geru", "lat_start": -10.9142, "lon_start": -37.0500, "lat_end": -10.9142, "lon_end": -37.0560},
        {"rua": "Rua São Cristóvão", "lat_start": -10.9138, "lon_start": -37.0490, "lat_end": -10.9138, "lon_end": -37.0580},
        {"rua": "Avenida Rio Branco", "lat_start": -10.9110, "lon_start": -37.0490, "lat_end": -10.9189, "lon_end": -37.0495},
        {"rua": "Rua Capela", "lat_start": -10.9130, "lon_start": -37.0522, "lat_end": -10.9189, "lon_end": -37.0522},
        {"rua": "Rua Propriá", "lat_start": -10.9165, "lon_start": -37.0500, "lat_end": -10.9165, "lon_end": -37.0570},
        {"rua": "Rua Santo Amaro", "lat_start": -10.9170, "lon_start": -37.0500, "lat_end": -10.9170, "lon_end": -37.0560},
        {"rua": "Praça General Valadão", "lat_start": -10.9110, "lon_start": -37.0510, "lat_end": -10.9122, "lon_end": -37.0515},
        {"rua": "Avenida Barão de Maruim", "lat_start": -10.9189, "lon_start": -37.0490, "lat_end": -10.9189, "lon_end": -37.0580},
        {"rua": "Rua Pacatuba", "lat_start": -10.9110, "lon_start": -37.0505, "lat_end": -10.9189, "lon_end": -37.0505},
        {"rua": "Rua Lagarto", "lat_start": -10.9110, "lon_start": -37.0560, "lat_end": -10.9189, "lon_end": -37.0560},
        {"rua": "Rua Estância", "lat_start": -10.9145, "lon_start": -37.0490, "lat_end": -10.9145, "lon_end": -37.0580},
        {"rua": "Rua Maruim", "lat_start": -10.9155, "lon_start": -37.0490, "lat_end": -10.9155, "lon_end": -37.0580},
    ]
    
    data = []
    
    # O CNEFE tem uma densidade absurda (praticamente porta a porta).
    # Vamos gerar centenas de pontos por rua, simulando um lote a cada ~8 metros.
    
    for i, via in enumerate(vias_reais):
        rua_nome = via["rua"]
        
        # Calcula a distância aproximada (em graus) da rua para determinar a quantidade de lotes
        dist_lat = abs(via["lat_end"] - via["lat_start"])
        dist_lon = abs(via["lon_end"] - via["lon_start"])
        dist_total = max(dist_lat, dist_lon)
        
        # Uma diferença de 0.001 grau é ~111 metros. A cada 8 metros temos um prédio.
        num_imoveis = max(10, int((dist_total / 0.001) * 14)) 
        
        for j in range(num_imoveis):
            t = j / max(1, (num_imoveis - 1))
            
            # Simulamos endereços nos dois lados da calçada (Lado Ímpar / Par)
            lado_rua = 1 if j % 2 == 0 else -1
            offset = 0.0001 # Cerca de 10 metros do centro da rua
            
            if dist_lat > dist_lon:
                # Rua Norte-Sul (offset na longitude)
                lat = via["lat_start"] + t * (via["lat_end"] - via["lat_start"])
                lon = via["lon_start"] + (offset * lado_rua)
            else:
                # Rua Leste-Oeste (offset na latitude)
                lat = via["lat_start"] + (offset * lado_rua)
                lon = via["lon_start"] + t * (via["lon_end"] - via["lon_start"])
            
            # Número do imóvel baseado na posição ao longo da via
            numero_imovel = int(t * 1500)
            if numero_imovel == 0: numero_imovel = np.random.randint(1, 10)
            endereco_completo = f"{rua_nome}, {numero_imovel}"
            
            # A base CNEFE classifica tipos de endereços (Domicílio Particular, Espaço Comercial, etc.)
            tipo_cnefe = np.random.choice(
                ["Domicílio Particular", "Estabelecimento Comercial", "Edificação em Construção/Ruína", "Estabelecimento de Saúde/Educação"], 
                p=[0.40, 0.50, 0.08, 0.02]
            )
            
            if tipo_cnefe == "Domicílio Particular":
                tipo = "Residencial"
            elif tipo_cnefe == "Edificação em Construção/Ruína":
                tipo = "Galpão" # Analogia visual
            else:
                if "Calçadão" in rua_nome or "Praça" in rua_nome:
                    tipo = np.random.choice(["Loja Térrea", "Sala Comercial"])
                else:
                    tipo = np.random.choice(["Loja Térrea", "Prédio Misto", "Sala Comercial"])
            
            # Atribuindo Uso de Solo Realístico
            if tipo == "Residencial":
                status = "Alugado" # Moradores
            elif tipo == "Galpão":
                status = np.random.choice(["Disponível", "Abandonado/IPTU Atrasado"], p=[0.3, 0.7])
            else:
                status = np.random.choice(["Alugado", "Disponível", "Abandonado/IPTU Atrasado"], p=[0.60, 0.25, 0.15])
            
            data.append({
                "id_espaco": f"CNEFE-2800308-{i}-{j}",
                "rua": endereco_completo,
                "tipo": tipo,
                "lat": lat,
                "lon": lon,
                "status_aluguel": status
            })
            
    df = pd.DataFrame(data)
    df.to_csv("data/cnefe_centro_aracaju.csv", index=False)
    print(f"Dataset CNEFE gerado com {len(df)} registros densos!")

if __name__ == "__main__":
    generate_cnefe_mock_csv()
