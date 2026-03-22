import pandas as pd
import numpy as np
import streamlit as st
import random

@st.cache_data(ttl=86400) # Mantém em cache por 1 dia
def load_data():
    np.random.seed(42)  # Manter a consistência espacial do mock
    random.seed(42)
    
    try:
        base_df = pd.read_csv("data/cnefe_centro_oficial.csv")
        
        # Recuperando as 6330 linhas completas para o card de métricas.
        # Para evitar o bug do zoom onde prédios verticais se sobrepõem perfeitamente
        # (causando o spiderfy de 200 pinos iguais), aplicamos um micro deslocamento (jitter).
        # 0.0001 graus de latitude/longitude equivale a ~11 metros (espalhando pelo terreno e calçada).
        np.random.seed(42)
        base_df['lat'] = base_df['lat'] + np.random.uniform(-0.00015, 0.00015, size=len(base_df))
        base_df['lon'] = base_df['lon'] + np.random.uniform(-0.00015, 0.00015, size=len(base_df))
        
    except Exception as e:
        st.error("Erro ao ler base CNEFE Oficial processada: " + str(e))
        return pd.DataFrame()
        
    data = []
    ruas_macro_dados = {}
    
    # Processando os 6.330 imóveis oficiais do IBGE CNEFE
    for i, row in base_df.iterrows():
        lat = row['lat']
        lon = row['lon']
        endereco_completo = str(row['rua'])
        rua_nome = endereco_completo.split(',')[0].strip()
        tipo_ibge = row['tipo_ibge']
        id_espaco = row['id_espaco']
        nome_estab = str(row['nome_estab'])
        
        # --- Traduzindo a taxonomia do IBGE (Uso de Solo) para a Visão Comercial Ficaqui ---
        if tipo_ibge == "Residencial":
            tipo = "Residencial"
            status = "Alugado"  # Pressupõe habitação ocupada predominantemente
        elif tipo_ibge == "Loja/Comércio/Serviço":
            tipo = np.random.choice(["Loja Térrea", "Sala Comercial"], p=[0.7, 0.3])
            status = np.random.choice(["Alugado", "Disponível", "Abandonado/IPTU Atrasado"], p=[0.50, 0.35, 0.15])
        elif tipo_ibge == "Galpão/Ruína/Obra":
            tipo = "Galpão"
            status = np.random.choice(["Disponível", "Abandonado/IPTU Atrasado"], p=[0.3, 0.7])
        else:
            tipo = "Prédio Misto"
            status = np.random.choice(["Alugado", "Disponível", "Abandonado/IPTU Atrasado"], p=[0.6, 0.2, 0.2])
            
        # Agrupamento macro (mesma rua compartilha fluxo e iluminação base)
        if rua_nome not in ruas_macro_dados:
            ilum = np.random.choice(["Boa", "Regular", "Ruim/Inexistente"])
            # Calçadões e grandes avenidas têm trânsito mais denso
            if "CALCADAO" in rua_nome.upper() or "PRACA" in rua_nome.upper() or "AVENIDA" in rua_nome.upper() or "AV " in rua_nome.upper():
                flux_base = np.random.randint(5000, 20000)
            else:
                flux_base = np.random.randint(500, 10000)
            ruas_macro_dados[rua_nome] = {"iluminacao": ilum, "fluxo": flux_base}
            
        iluminacao = ruas_macro_dados[rua_nome]["iluminacao"]
        fluxo = ruas_macro_dados[rua_nome]["fluxo"] + np.random.randint(-150, 150)
            
        # Dados fiscais / venda
        if status == "Alugado":
            receita = np.random.randint(15000, 450000)
        else:
            receita = 0
            
        potencial = round(np.random.uniform(0.4, 0.98), 2)
        
        # Anexa o nome do estab (se oficial) ao ID visual para facilitar pro usuario
        if nome_estab and str(nome_estab) != 'nan':
            label_id = str(nome_estab)
        else:
            label_id = endereco_completo
            
        data.append({
            "id_espaco": label_id, # Aqui trocamos o ID IBGE duro pelo Label Limpo para o Front-End
            "rua": endereco_completo,
            "tipo": tipo,
            "lat": lat,
            "lon": lon,
            "status_aluguel": status,
            "iluminacao": iluminacao,
            "receita_gerada": receita,
            "fluxo_pessoas_dia": max(0, fluxo),
            "potencial_retrofit": potencial
        })

    return pd.DataFrame(data)
