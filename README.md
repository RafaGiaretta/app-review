# API-BUSCA

Um projeto para coleta, análise de sentimentos e sugestões baseadas em dados.  
Abaixo está a descrição da estrutura do projeto e suas funcionalidades principais.

---

## 🗂️ Estrutura do Projeto

app/modules/

- coleta.py # Coleta de dados
- core.py # Lógica central do projeto
- sentiments.py # Análise de sentimentos de textos
- sugestocs.py # Geração de sugestões baseadas nos dados
- .env # Variáveis de ambiente (API keys, configs sensíveis)
- config.py # Configurações do projeto
- main.py # Ponto de entrada da aplicação (inicia o servidor)
- requirements.txt # Lista de dependências do projeto

## Como Executar

### Instalação

1. Instale as Dependências:

   ```bash
   pip install -r requirements.txt

   ```

2. Configure as variáveis de ambiente:
   ```
   Renomeie .env.exemplo para .env e preencha as variáveis
   ```

### Configuração

- .env: Aramazena as chaves de API, credenciais e configurações sensíveis.
- config.py: Define configurações gerais.

### Funcionalidades principais

- Coletar dados de fontes externas (Web scraping).
- Analisa sentimentos de textos usando técnica de NLP.
- Gera sugestões personalizadas com base nos dados processados.
- Dispinibiliza endpoints para interação via API
