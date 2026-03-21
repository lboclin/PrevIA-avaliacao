# PrevIA: Sistema de Inteligência de Pesquisa

O **PrevIA** é um sistema agêntico construído com [LangGraph](https://python.langchain.com/docs/langgraph/) que orquestra múltiplos agentes de IA (Pesquisador, Analista, Redator e Revisor) para coletar dados, analisar informações e redigir relatórios de inteligência a partir de um tópico fornecido pelo usuário. O sistema também inclui intervenção humana (Human-in-the-Loop) em caso de loops de execução.

## Como rodar o projeto

### Pré-requisitos
- **Python 3.10+** instalado.

### Passo a passo

1. **Clone o repositório:**
   ```bash
   git clone <URL_DO_SEU_REPOSITORIO>
   cd <NOME_DA_PASTA_DO_REPOSITORIO>
   ```
2. **Crie e ative um ambiente virtual (recomendado):**
    ```
    python -m venv venv
    ```
    #### No Windows:
    ```
    venv\Scripts\activate
    ```
    #### No Linux/macOS:
    ```
    source venv/bin/activate
    ```
3. **Instale as dependências:**
    ```
    pip install -r requirements.txt
    ```
4. **Configuração de Ambiente:**
    Renomeie o arquivo .env.example para .env (ou crie um novo arquivo .env).
    Insira suas chaves de API:
    ```
    OPENAI_API_KEY=sua_chave_aqui
    TAVILY_API_KEY=sua_chave_aqui
    ```
5. **Execute o sistema:**
    ```
    python my_agent/agent.py
    ```
Ao rodar, o sistema solicitará o tópico de pesquisa desejado no terminal. Os relatórios gerados serão salvos na pasta intelligence_reports.