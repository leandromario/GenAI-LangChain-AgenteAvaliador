# GenAI-LangChain-AgenteAvaliador

Projeto acadêmico desenvolvido na especialização em **Inteligência Artificial Generativa** da **UPFR**, na disciplina de **LangChain**, ministrada pelo professor **Vinícius Fulber Garcia**.

## Sobre o trabalho

Primeiro trabalho da disciplina: a partir das avaliações obtidas da API, conforme o código do repositório, desenvolver um agente que indique se a avaliação é positiva ou negativa.

## Estrutura do repositório

| Arquivo | Descrição |
|---|---|
| `agente_avaliacoes.py` | Script principal, com todo o código do agente. |
| `pyproject.toml` | Configuração do Poetry e dependências (`langchain`, `langchain-groq`, `python-dotenv`, `requests`). Requer Python 3.11 ou superior. |
| `poetry.lock` | Versões travadas das dependências. |
| `README.md` | Este arquivo. |
| `.gitignore` | Arquivos ignorados pelo Git (inclui o `.env`). |

## Como funciona

1. Busca as avaliações em `https://apis.codante.io/api/reviews-api/reviews` e extrai o campo `description` de cada uma.
2. Carrega a chave `GROQ_API_KEY` do arquivo `.env` e cria o modelo `ChatGroq` com `temperature=0`, para que a classificação seja a mais determinística possível.
3. Monta chains do LangChain com `ChatPromptTemplate | llm | StrOutputParser`:
   - **Chain 1:** classifica a avaliação como `Positiva` ou `Negativa`.
   - **Chains 2 e 3:** geram uma resposta curta de atendimento de uma loja de fones de ouvido, de acordo com a classificação. Para avaliações positivas, a resposta é cordial e agradecida. Para as negativas, é empática, pede desculpas e oferece ajuda.
4. Para cada avaliação, imprime a avaliação, a classificação e a resposta gerada. Se a classificação não for reconhecida, nenhuma resposta é gerada.

## Como executar

### Pré-requisitos

- Python 3.11 ou superior
- [Poetry](https://python-poetry.org/)
- Uma chave de API da [Groq](https://console.groq.com/)
- Conexão com a internet, para acessar a API de avaliações e a Groq

### Passo a passo

1. Crie um arquivo `.env` na raiz do projeto com a sua chave:

   ```
   GROQ_API_KEY=sua_chave_aqui
   ```

2. Instale as dependências:

   ```bash
   poetry install
   ```

3. Execute o script:

   ```bash
   poetry run python agente_avaliacoes.py
   ```

## Observações

- O modelo configurado no script (`qwen/qwen3.8-27b`) precisa estar disponível na sua conta da Groq. Caso contrário, ajuste o nome do modelo em `agente_avaliacoes.py`.
- Se o `poetry install` recusar o valor `requires-python = "^3.11"` do `pyproject.toml`, use `>=3.11,<4.0`.

## Limitação encontrada: limite de tokens da Groq

No plano gratuito (`on_demand`) da Groq, o modelo `qwen/qwen3.8-27b` aceita no máximo **1000 tokens de saída por minuto (OTPM)**. Sem `max_tokens` definido, o `ChatGroq` reserva uma saída esperada maior que esse limite, e a requisição é recusada antes de ser executada:

```
groq.RateLimitError: Error code: 429 - Request too large for model `qwen/qwen3.8-27b` ...
on output tokens per minute (OTPM): Limit 1000, Requested 1034.
```

### Ajuste aplicado

Em `agente_avaliacoes.py`:

- **`max_tokens = 200`** no `ChatGroq`: limita a saída de cada requisição, que fica abaixo do limite por minuto. A classificação usa poucos tokens e a resposta tem até 3 frases.
- **`max_retries = 5`** no `ChatGroq`: repete a chamada com espera quando a Groq responde com erro 429.
- **`time.sleep(10)`** ao final de cada iteração do loop: espaça as chamadas para respeitar o limite de tokens por minuto.

Com isso, a execução fica mais lenta, pois cada avaliação leva pelo menos 10 segundos. Para processar muitas avaliações mais rápido, é possível usar um modelo com limite maior ou migrar para o Dev Tier da Groq.
