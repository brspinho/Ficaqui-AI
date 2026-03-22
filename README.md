# 🏙️ Projeto Ficaqui: Ecossistema de Inteligência Urbana

O Ficaqui é uma plataforma de decisão baseada em dados que conecta o poder público (Prefeitura), o capital privado (Fundos de Investimento) e o cidadão para reocupar o Centro de Aracaju. Este MVP é focado no Pilar de **Cérebro (Ficaqui AI)**, cruzando microdados de transporte, demografia e segurança para instruir ações de **Políticas Públicas** e atração do **Fundo Imobiliário (Músculo)** focando em Moradia de Uso Misto.

## 🚀 Como Rodar o Programa (Dashboard B2G Modular)

Nossa aplicação foi refatorada para uma arquitetura modular focada em performance e escalabilidade. Adotamos o **uv** como gerenciador de dependências e ambiente virtual, por ser extremamente rápido.

### 1. Pré-requisitos
- Ter o [Python](https://www.python.org/downloads/) instalado.
- Instalar o gerenciador `uv` globalmente caso ainda não possua:
  ```powershell
  # No Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  *(Obs: Lembre-se de reiniciar o terminal ou exportar o PATH conforme instruído pelo instalador do uv)*

### 2. Instalação e Execução (Tudo em um comando)
O `uv` gerencia o ambiente virtual automaticamente. Navegue até a pasta do dashboard e rode o projeto:

```bash
cd ficaqui_dashboard
uv run streamlit run app.py
```
*(Na primeira execução, o uv baixará todas as dependências do `requirements.txt` automaticamente em milissegundos)*

### 3. Configuração da IA (Groq)
Para habilitar o Chatbot B2G, coloque sua chave da API Groq pela aba lateral (Sidebar) dentro do app ou crie um arquivo `.env` dentro de `ficaqui_dashboard/`:
```env
GROQ_API_KEY=sua_chave_aqui
```

### 4. Acessando a Plataforma
Após o carregamento, a aplicação geralmente abrirá o seu navegador padrão automaticamente. Caso contrário, acesse através do link abaixo:
👉 **[http://localhost:8501](http://localhost:8501)**