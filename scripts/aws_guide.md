# Guia de Deploy AWS: Ficaqui-AI (App Runner + Docker)

Este guia orienta o deploy do Ficaqui-AI usando **AWS App Runner**, que é a forma mais moderna e performática de rodar Streamlit na AWS.

## Passo 1: Preparar o Registro de Container (Amazon ECR)
1. Acesse o Console AWS e procure por **Elastic Container Registry (ECR)**.
2. Clique em **Create repository**.
3. Nomeie como `ficaqui-ai` e mantenha as configurações padrão. Clique em **Create**.
4. Guarde a URI do repositório (ex: `123456789012.dkr.ecr.us-east-1.amazonaws.com/ficaqui-ai`).

## Passo 2: Configurar o GitHub Actions (Secrets)
No seu repositório do GitHub:
1. Vá em **Settings** > **Secrets and variables** > **Actions**.
2. Adicione os seguintes Secrets:
   - `AWS_ACCESS_KEY_ID`: Seu ID de chave de acesso AWS.
   - `AWS_SECRET_ACCESS_KEY`: Sua chave secreta AWS.
   - `AWS_REGION`: Ex: `us-east-1`.
   - `ECR_REPOSITORY`: `ficaqui-ai`.

## Passo 3: Criar o Serviço no App Runner
1. No Console AWS, vá para **AWS App Runner**.
2. Clique em **Create service**.
3. Em **Source**, selecione **Container registry**.
4. Em **Provider**, escolha **Amazon ECR**.
5. Selecione a imagem que foi subida pelo GitHub Actions (ou suba uma manualmente pela primeira vez).
6. Em **Deployment settings**, escolha **Automatic** (isso fará o deploy a cada push no ECR).
7. Em **Service configuration**, defina a porta como `8501`.
8. Clique em **Create & Deploy**.

## Passo 4: CI/CD Automático
O arquivo `.github/workflows/deploy.yml` que criei cuidará de:
1. Buildar a imagem Docker a cada `push` na branch `main`.
2. Pushar para o ECR.
3. O App Runner detectará a nova imagem e atualizará o site automaticamente.

---
*Dica: Se o mapa ainda estiver pesado, verifique se o Samuel usou Pydeck para aceleração WebGL!*
