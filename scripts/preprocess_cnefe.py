import pandas as pd

def process_cnefe():
    print("Lendo 50MB do CNEFE bruto...")
    df = pd.read_csv("data/2800308_ARACAJU.csv", sep=";", encoding="utf-8", dtype=str)
    
    print("Filtrando bairro CENTRO...")
    # Em algumas bases o bairro pode vir com espaços ou variações
    df_centro = df[df['DSC_LOCALIDADE'].str.strip().str.upper() == 'CENTRO'].copy()
    
    if len(df_centro) == 0:
        print("Aviso: 'CENTRO' exato não encontrado. Tentando conter 'CENTRO'.")
        df_centro = df[df['DSC_LOCALIDADE'].str.contains('CENTRO', na=False, case=False)].copy()
        
    print(f"Encontrados {len(df_centro)} endereços oficiais no Centro.")
    
    # Criar colunas otimizadas para o loader.py
    # Formando a rua: RUA + TITULO + NOME
    tipo_logr = df_centro['NOM_TIPO_SEGLOGR'].fillna('')
    tit_logr = df_centro['NOM_TITULO_SEGLOGR'].fillna('')
    nome_logr = df_centro['NOM_SEGLOGR'].fillna('')
    num = df_centro['NUM_ENDERECO'].fillna('SN')
    
    rua_completa = tipo_logr + " " + tit_logr + " " + nome_logr
    # Limpar duplos espaços
    rua_completa = rua_completa.str.replace('  ', ' ').str.strip()
    
    # Formar dicionario simplificado
    data = []
    
    for i, row in df_centro.iterrows():
        # Código de espécie IBGE 2022:
        # 1: Domicílio particular
        # 2: Domicílio coletivo
        # 3: Estabelecimento agropecuário
        # 4: Estabelecimento de ensino
        # 5: Estabelecimento de saúde
        # 6: Estabelecimento de outras finalidades (Comercial, Serviço)
        # 7: Edificação em construção
        # 8: Estabelecimento religioso
        
        cod_esp = str(row['COD_ESPECIE'])
        tipo = "Desconhecido"
        
        if cod_esp == '1':
            tipo = "Residencial"
        elif cod_esp == '6':
            # Comercial/Serviço
            tipo = "Loja/Comércio/Serviço"
        elif cod_esp == '7':
            tipo = "Galpão/Ruína/Obra"
        elif cod_esp == '8':
            tipo = "Religioso"
        elif cod_esp == '4' or cod_esp == '5':
            tipo = "Serviço Público/Privado"
        else:
            tipo = "Misto/Outros"
            
        data.append({
            "id_espaco": f"IBGE-{row['COD_UNICO_ENDERECO']}",
            "rua": f"{rua_completa.loc[i]}, {num.loc[i]}",
            "tipo_ibge": tipo,
            "lat": pd.to_numeric(row['LATITUDE'], errors='coerce'),
            "lon": pd.to_numeric(row['LONGITUDE'], errors='coerce'),
            "nome_estab": str(row['DSC_ESTABELECIMENTO']) if pd.notna(row['DSC_ESTABELECIMENTO']) else ""
        })
        
    df_clean = pd.DataFrame(data)
    # Filtra onde a lat/lon falhou
    df_clean = df_clean.dropna(subset=['lat', 'lon'])
    
    df_clean.to_csv("data/cnefe_centro_oficial.csv", index=False)
    print("Salvo em data/cnefe_centro_oficial.csv !!")

if __name__ == "__main__":
    process_cnefe()
