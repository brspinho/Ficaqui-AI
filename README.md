# 🏙️ Ficaqui

> Para revitalizar o centro de Aracaju não precisa ir longe, Ficaqui.

---

## 📌 Sobre o Projeto

O **Ficaqui** é uma plataforma de decisão baseada em dados criada durante o **Hackathon Centrolab**. O foco absoluto do projeto é a **revitalização do comércio do Centro de Aracaju**, conectando o poder público, o capital privado e o ecossistema local para reaquecer a economia e ocupar os espaços ociosos.

## 💡 Nossa Tese de Solução

Acreditamos que a solução definitiva para o esvaziamento do Centro **não é apenas um software**, mas sim a aplicação de **Políticas Públicas estruturadas** (como incentivos de ICMS, PPPs, Retrofit e novos marcos fiscais).

O painel **Ficaqui** atua como um **Instrumento de Inteligência e Informação**, municiando os gestores com dados preditivos e espaciais para fundamentar decisões estratégicas e avaliar o impacto de incentivos na rede de comércio.

---

## 🛠️ Funcionalidades Principais

### 🗺️ Painel de Controle Espacial (Dashboard B2B2G)

Uma interface geográfica que permite alternar entre lentes de análise:

- **Visão Micro (Lotes/Imóveis)**: Detalhamento de cada ponto comercial. Exibe status (Alugado, Disponível, Abandonado), volume de pedestres (VPT), iluminação pública e indicadores de segurança.
- **Visão Macro (Mapas de Calor)**: Camadas termográficas configuráveis para:
  - Fluxo de Pessoas (Pedestres/Dia)
  - Oportunidades de Retrofit e Investimento
  - Risco por Iluminação Noturna
  - Estatísticas de Segurança (Crimes/Mês, Cobertura Policial)

### 🤖 Inteligência Ficaqui AI (Chatbot B2B2G)

Um analista urbanista generativo conectado a LLMs (Groq/Llama) que:

- Cruza microdados urbanos com metas de fomento ao comércio.
- Justifica a criação de incentivos estaduais (créditos ICMS reversos) e PPPs em prédios ociosos. e.g., "Instalar um Hub comercial de rua no Prédio X se justifica pelo fluxo pedonal da Rua Y...".

---


### 📄 Relatórios e Pareceres Executivos (PDF/DOCX)
Filtre a inteligência espacial e exporte diagnósticos oficiais:
*   **Filtragem Dinâmica**: Recorte por Status de Ocupação e Tipologia de Imóvel.
*   **Geração de Pareceres (Groq IA)**: Emissão de sínteses executivas automáticas que diagnosticam a vacância e propõem medidas urbano-fiscais.
*   **Multi-formato**: Download instantâneo do parecer em **PDF** ou **Word (DOCX)**, além da base de dados analítica em **CSV**.

---

## 📊 Arquitetura de Dados

O sistema opera um motor de simulação que se apoia em:

- **CNEFE (IBGE)**: Cadastro Nacional de Endereços para consistência posicional e tipologia.
- **Mapeamento de Prédios Estratégicos**: Cadastro de ativos estatais/federais (Ex: Hotel Palace, INSS) com potencial de âncoras comerciais.
- **Ecossistema Preditivo**: Modelagem de correlação entre Status do Imóvel, Iluminação e Segurança versus Atração de Fluxo Comercial.

---

## 🚀 Como Rodar o Dashboard

Siga os passos abaixo para executar a aplicação Streamlit:

### 1️⃣ Pré-requisitos

Instale o [Python](https://www.python.org/downloads/) (Recomendado 3.10+).

### 2️⃣ Instalação das Dependências

No terminal, na pasta raiz do projeto:

```bash
pip install streamlit pandas folium streamlit-folium plotly groq python-dotenv
```

### 3️⃣ Configuração (IA/Chatbot)

Para usar o **Ficaqui AI**, certifique-se de que o arquivo `.env` na raiz contenha sua chave de API:

```env
GROQ_API_KEY="sua_chave_aqui"
```

### 4️⃣ Execução

```bash
python -m streamlit run main.py
```

Acesse em: 👉 **[http://localhost:8501](http://localhost:8501)**

---

_Uma iniciativa para o futuro do Centro de Aracaju._
