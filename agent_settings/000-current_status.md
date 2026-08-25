# Status Corrente do Plano de Estudos

> Documento de **memória de trabalho**. Descreve o que já foi executado, o que ficou pendente e quais decisões de design foram tomadas.
> Deve ser **lido a cada mensagem** antes de responder, e **atualizado a cada mensagem em que houver progresso real** de código, configuração ou estado do plano. Ver "Protocolo de memória viva" no `CLAUDE.md`.

**Última atualização:** 2026-08-24 (retomada — `call_rag_node` e `call_logs_node` completos e validados; `call_logs_node` rodou de ponta a ponta com client+server MCP reais pela primeira vez no projeto, após depurar 7 bugs (imports, arquitetura client vs. server, 2 erros de execução reais, 1 problema de infra, 1 bug de framing herdado do Dia 2, 1 divergência de tipo); faltam nós `A`/`D` e a montagem do grafo — ver seção 1)
**Posição no plano:** Semana 1 — Dia 2 (MCP) estruturalmente completo (caminhos de arquivo atualizados após a reorganização em pacotes: `mcp_server/context_lifespan.py`, `mcp_server/mcp_server_provider.py`, `mcp_server/logs_mcp.py`, `entrypoints/logs_query_mcp_demo.py`). Falta rodar o entrypoint mais uma vez de verdade (só a cadeia de import foi revalidada nesta sessão, não o `mcp.run()` propriamente) e o teste automatizado (`pytest`). Dia 3 (LCEL) avançou bastante em 2026-08-19: pacotes `langchain-core`/`langchain-openai` instalados, `entrypoints/lcel_demo.py` funcional integrando o RAG do Dia 1 com uma chain real. Dia 1 (pytest da cosine similarity) e o teste automatizado do Dia 2 seguem em aberto — mesmo padrão de "avançar e voltar depois" já usado antes (ver seções 1 e 4).

### Sessão 2026-08-19 — retomada do Dia 3 (LCEL), instalação dos pacotes

- **Dependências instaladas pelo aluno:** `langchain-core>=1.5.6` e `langchain-openai>=1.5.2` adicionadas a `src/pyproject.toml` via `uv add` (rodado pelo próprio aluno, conforme regra do `CLAUDE.md`). Chegou aos dois nomes de pacote por dedução própria: primeiro `langchain-openai` (conector específico do provider), depois `langchain-core` (motor genérico do `Runnable`/pipe) — ambos via transferência da convenção `framework-especialização` já usada com `python-dotenv` e da separação genérico/específico já usada com `asyncpg`/ADO.NET.
- **Ainda não escrito:** nenhum código da chain `Prompt | Model | Parser` do Dia 3 existe em `src/` ainda — só os pacotes foram instalados.

### Sessão 2026-08-18 — construção de `mcp_server_provider.py` e `context_lifespan.py`

- **`src/context_lifespan.py` (novo, concluído):** `LifespanContext`, `@dataclass` com campo único `pool: asyncpg.Pool`, docstring em português. Sem dependência de outros arquivos do projeto.
- **`src/mcp_server_provider.py` (novo, `lifespan()` concluída):** função completa — cria `asyncpg.Pool` via `POSTGRES_CONNECTION_STRING` (de `environment_setting`), `yield LifespanContext(pool=pool)` dentro de `try`, `pool.close()` no `finally` (proteção contra exceção dentro do `async with`, adicionada por iniciativa própria do aluno). Solução final inlinou `LifespanContext(pool=pool)` direto no `yield`, evitando colisão de nome com a própria função `lifespan`. Falta só: instanciar `mcp = MCPServer(name=..., lifespan=lifespan)` no mesmo arquivo.
- **Dívida de conexão do Postgres já resolvida:** `environment_setting.py` ganhou `POSTGRES_CONNECTION_STRING = _required("POSTGRES_CONNECTION_STRING")`; aluno adicionou o valor no próprio `.env` (fora do escopo do agente, conforme `CLAUDE.md` item 7).
- **`mcp_server_provider.py` concluído:** `mcp = MCPServer(lifespan=lifespan, name="LogsQueryServer")` — nome escolhido pelo aluno após reconsiderar `LogsDatabaseServer` como amplo demais pro escopo real (só uma tool, só leitura, só `service_logs`).
- **`logs_dao.py` desbloqueado:** import `from mcp_server_provider import mcp` adicionado — `@mcp.tool()` agora resolve. Arquivo funcionalmente completo (nenhuma pendência de código conhecida).
- **`src/logs_query_mcp_starter.py` (novo, concluído) — entrypoint do servidor MCP**, separado do `main.py` (que continua sendo a demo do RAG do Dia 1 — decisão do aluno, motivada pela natureza bloqueante de `mcp.run()` vs. o fluxo de `main.py` que termina sozinho): importa `mcp` de `mcp_server_provider`, importa o módulo de tools/resources só pelo efeito colateral do registro via `@mcp.tool()`/`@mcp.resource()` (marcado com `# noqa: F401`, adicionado por iniciativa do próprio aluno), e chama `mcp.run()` (confirmado no SDK: default `transport="stdio"`, batendo com o que foi deduzido no Dia 2 sobre transporte) dentro do guard `if __name__ == "__main__":`.
- **Cadeia de dependência do Dia 2 (MCP) estruturalmente completa e testada em execução real:** `context_lifespan.py` → `mcp_server_provider.py` → `logs_dao.py` (nome na época) → `logs_query_mcp_starter.py`. Aluno rodou `uv run logs_query_mcp_starter.py` no próprio terminal — sem erro, `Pool` conectou no Postgres (`POSTGRES_CONNECTION_STRING` corrigido de `.../postgres` para `.../microservices_logs`, banco errado apontado inicialmente), execução parou no `yield` e travou em `mcp.run()` esperando stdio, exatamente como previsto pela teoria do Dia 2. **Ainda não testado:** uma LLM/client MCP real invocando a tool (nenhum client conectado ainda, só validação de que o processo sobe).
- **Tabela `service_logs` populada (2026-08-18):** 10 linhas de exemplo inseridas via `psql` pelo aluno, cobrindo 4 serviços (`payment-service`, `checkout-service`, `inventory-service`, `notification-service`), os 4 níveis (`INFO`/`WARN`/`ERROR`/`TIMEOUT`), datas de 01/08 a 16/08, e mensagens com termos distintos — pensado pra exercitar cada filtro de `query_logs` individualmente.
- **Resource `get_logs_table_schema` criado** (`@mcp.resource("resource://logs/table/schema")`), expondo as 8 colunas de `service_logs` com tipo real (verificado via `\d service_logs` no `psql` — corrigiu um chute errado de `id: UUID`; na real, `id` é `integer` autoincrementado via sequence, e `correlation_id` é o `uuid`) e descrição de cada coluna. Desambiguação explícita adicionada na descrição de `origin` pra evitar confusão com o parâmetro `origin` da tool `query_logs` (que na verdade filtra a coluna `service`, não a coluna `origin`).
- **`logs_dao.py` renomeado para `logs_mcp.py`:** aluno questionou se "DAO" ainda fazia sentido depois que o arquivo passou a misturar acesso a dados com exposição MCP (`@mcp.tool()`/`@mcp.resource()`/`Context`, todos específicos do SDK — um DAO clássico é desacoplado de protocolo). Decidiu manter tudo fundido por ora e renomear pra refletir a realidade; separação futura (DAO puro + arquivo de wiring MCP) registrada como dívida técnica (seção 4). Import atualizado em `logs_query_mcp_starter.py` (`import logs_mcp`).
- **Decisão de nome da função de lifecycle:** function chamada `lifespan` (não `get_lifespan`, não `Get`) — motivo: não é uma factory (que usaria verbo `create_`/`build_`/`make_`), é um hook de ciclo de vida passado por referência para `MCPServer(lifespan=...)`; convenção observada no próprio SDK é nomear a função igual ao parâmetro que a recebe.
- **Convenção de nomenclatura de arquivo reforçada:** módulos Python em `snake_case` (PEP 8), nunca `PascalCase` — aluno errou uma vez (`ContextLifespan.py` → `context_lifespan.py`) e uma vez em nome de função (`Get` → `lifespan`), corrigiu nas duas quando questionado sobre a convenção.
- **Nova dívida técnica identificada (não resolvida ainda):** `environment_setting.py` só valida `OPENAI_API_KEY` e `LANGSMITH_API_KEY` — não há nenhuma variável de ambiente para a conexão com o Postgres (host/porta/user/senha/banco), necessária pra `asyncpg.create_pool()` dentro do `lifespan`.
- **Gap arquitetural identificado (não resolvido ainda):** `logs_dao.py` importa `mcp` de `mcp_server_provider.py`, mas nada importa `logs_dao.py` de volta — sem esse import em algum entrypoint, o decorator `@mcp.tool()` nunca roda e a tool nunca se registra no servidor. Entrypoint ainda não decidido nem criado.

**Nota de processo:** o comando `uv add mcp` foi executado pelo agente diretamente, o que violou a preferência do aluno de rodar ele mesmo os comandos de configuração de ambiente (parte do aprendizado). Instrução registrada em `CLAUDE.md` (seção 1, item 7) para não se repetir. O aluno optou por deixar a instalação como está em vez de reverter.

### Infraestrutura de banco (Dia 2 — tool de logs), 2026-08-11

- Container Postgres `mcp-logs-db` (imagem `postgres:16`) rodando no Docker do WSL do aluno, porta `5432`, banco `microservices_logs`. Subido pelo próprio aluno (comando fornecido pelo mentor, não executado pelo agente — conforme `CLAUDE.md` item 7).
- Schema decidido de forma socrática: aluno propôs `timespent`/`correlationId`/`message`, guiado a completar com `service_src` (+ origem classe/método) e `created_datetime`; coluna `level` (severidade) veio de recomendação direta do mentor (padrão de mercado / compatibilidade Datadog), a pedido explícito do aluno.
- Tabela `service_logs` criada com sucesso pelo aluno via `psql` dentro do container: `id, created_at, service, origin, level (CHECK IN INFO/WARN/ERROR/TIMEOUT), message, duration_ms, correlation_id`.
- **Driver Python decidido:** `asyncpg` (assíncrono nativo), em vez de `psycopg2` síncrono — justificativa: SDK do MCP já é assíncrono por baixo (starlette/anyio vieram junto na instalação), e uma chamada síncrona ao banco bloquearia a thread. **Instalado em 2026-08-13** (`asyncpg==0.31.0`, via `uv add asyncpg` rodado pelo aluno).

Sessão de 2026-08-13 revisitou o papel do `asyncpg` por analogia com ADO.NET: aluno reconstruiu a distinção entre a camada genérica (interfaces `IDbConnection`/`IDbCommand` do ADO.NET) e a camada de provider específico por SGBD (`Npgsql`/`Microsoft.Data.SqlClient`), e concluiu sozinho — após ser corrigido sobre achar que a diferença era "específico vs. genérico" no nível errado — que `asyncpg` ocupa a posição de provider (camada específica), sem uma camada de interface genérica equivalente por cima no ecossistema Python assíncrono.

### Tool `query_logs` (`src/logs_dao.py`) — estado em 2026-08-13

Implementada com: assinatura tipada (todos os 5 filtros opcionais via `Tipo | None = None`), `level` restrito via `Literal["INFO","WARN","ERROR","TIMEOUT"]`, docstring orientando a LLM sobre uso de cada filtro, `WHERE` dinâmico com duas listas paralelas (`conditions`/`params`, mesmo motivo da decisão 4 da seção 3), conexão via `pool.fetch(...)` (método de conveniência do `asyncpg.Pool`, sem precisar de `acquire()` manual), e retorno `[dict(row) for row in rows]` (converte `asyncpg.Record` — que não é `dict` nativo — pra ficar serializável em JSON e satisfazer o tipo `list[dict]`).

**Estado em 2026-08-13 (fim de sessão):** `src/logs_dao.py` tem imports corretos (`datetime`, `typing.Literal`, `Context` de `mcp.server.mcpserver` — não `mcp.server.fastmcp`, ver correção de API abaixo) e corpo funcional completo. Falta só a instância `mcp` (`@mcp.tool()` na linha 7 ainda não resolve — `mcp` não existe em nenhum arquivo do projeto ainda) e o `lifespan` que a alimenta.

**Correção de API registrada (2026-08-13):** o pacote `mcp>=2.0.0` instalado usa `MCPServer` (não `FastMCP`) em `mcp.server.mcpserver` (não `mcp.server.fastmcp`) — nome mudou entre versões do SDK. Detalhe completo em `003-current_environment.md`. Ao retomar, checar sempre `src/.venv/Lib/site-packages/mcp/` antes de citar API desse pacote.

**Retomar por (atualizado 2026-08-18, fim de sessão):**
1. Rodar `logs_query_mcp_starter.py` de novo pra validar que o `resource` novo não quebrou nada (import, registro) — ainda não testado desde que `get_logs_table_schema` foi adicionado.
2. Teste automatizado (`pytest` + SQLite in-memory ou mock de `pool`) cobrindo `query_logs` (query válida/inválida) e `get_logs_table_schema`.
3. Único item do checklist original do Dia 2 ainda em aberto além de testes: nenhum — dados de exemplo e exposição de schema concluídos nesta sessão.

### Semana 2 — Dia 1: LangGraph — estado desenhado, ainda não implementado (2026-08-19)

Aluno decidiu avançar direto pra Semana 2 no mesmo dia, deixando o pytest do Dia 3 e as dívidas de Dia 1/Dia 2 em aberto. Antes de entrar no design, validamos pré-requisito (regra do `CLAUDE.md` item 3): `TypedDict` nunca tinha sido tocado — aluno não conhecia, mas deduziu corretamente por analogia com interface do C# que é "um contrato"; corrigido o ponto-chave de que `TypedDict` **não tem nenhuma checagem em tempo de execução** (diferente de interface do C#, checada pelo compilador) — é só metadado pra type checkers estáticos (mypy/pyright/IDE). Testado e confirmado empiricamente que `= None` dentro de um `TypedDict` **não cria valor padrão nenhum** (`__required_keys__` continua marcando a chave como obrigatória) — o mecanismo certo pra chave opcional é `NotRequired[...]`, ainda não escrito em código.

**Estado desenhado (conceitual, só na conversa, código pendente):**
```python
class State(TypedDict):
    user_message: str
    rag_response: NotRequired[list[str] | None]   # nem toda pergunta aciona o RAG
    related_logs: NotRequired[list[dict] | None]  # nem toda pergunta aciona a busca de logs (MCP)
    inference_result: str                         # sempre presente — a LLM sempre responde algo, mesmo "não sei"
```

Raciocínio do aluno vale registrar: `related_logs: list[dict]` porque cada linha de log do Postgres já vira um `dict` ao ser lida (mesma tradução que a tool `query_logs` do Dia 2 já faz); `rag_response: list[str]` (não só um termo) porque a busca já é parametrizável por `top_k` em `search_for_embedding` — não faz sentido travar o estado a só 1 resultado. `inference_result` não é opcional porque, independente de quais nós rodarem, o grafo sempre termina gerando alguma resposta pro usuário.

**Nome do pacote decidido (2026-08-24): `orchestration/`**, não `graph/`. Aluno propôs `graph/` (nome da ferramenta, LangGraph); questionado se `rag/`/`mcp_server/` nomeiam responsabilidade ou biblioteca, convergiu para `orchestration/` — mantém a convenção dos dois pacotes existentes (nome descreve o que o pacote faz: decidir quando acionar RAG e/ou a tool MCP e combinar em `inference_result`), não a tecnologia usada por baixo (LangGraph). Verificado que não havia risco de colisão de nome com pacote instalado (`langgraph` ainda não está no `.venv` nesta sessão) — motivo diferente do que gerou a troca `mcp/` → `mcp_server/`.

**`src/orchestration/` criado (2026-08-24):** `__init__.py` + `state.py` com `State(TypedDict)` completo (aluno escreveu o corpo sozinho, mentor só apontou a falta do import de `TypedDict`/`NotRequired` de `typing` quando questionado — aluno reconheceu que faltava import mas não sabia qual).

**Topologia do grafo decidida (2026-08-24), por dedução do aluno:**
- Nó `A` (entrada/decisão) — aresta condicional pra `B`, `C`, ambos (fan-out) ou `D` sozinho.
- Nó `B` (busca em logs, via MCP) — aresta incondicional pra `D`.
- Nó `C` (busca no RAG) — aresta incondicional pra `D`.
- Nó `D` (saída).
Trajetória de raciocínio: proposta inicial tinha um nó `Evaluate` fazendo `A -> B -> Evaluate -> C -> Evaluate -> D` (execução sequencial com reavaliação); questionado sobre paralelismo em sistemas distribuídos (`Task.WhenAll`/scatter-gather, que ele já usou em C#), transferiu o padrão sozinho e concluiu que uma aresta condicional pode devolver **lista** de destinos (`["B","C"]`), eliminando o `Evaluate`. Também concluiu sozinho, sob pergunta, que `D` só é retornado pela função condicional de `A` **quando nem `B` nem `C` são necessários** — nunca junto com eles (senão `D` rodaria antes da busca terminar).

**`orchestration/nodes.py` criado (2026-08-24) — `call_rag_node` completo e correto.** Assinatura `def call_rag_node(state: State) -> dict:` chegou por dedução do aluno via analogia com middleware ASP.NET Core (recebe `state`, mas — diferente do middleware, que muta o `HttpContext` — devolve um `dict` parcial novo; motivo explicado pelo mentor a pedido do aluno: nós rodando em paralelo via fan-out não podem mutar o mesmo objeto sem risco do mesmo bug de "sobrescrita silenciosa" já visto no Dia 1). Depuração guiada por perguntas, sem correção pronta, corrigiu sozinho quatro bugs próprios em sequência: (1) variável local nomeada `dict`, sombreando o builtin; (2) tentativa de indexar o resultado de `search()` por chave string (`["term"]`) achando que era uma lista de dicts, quando na real é lista de tuplas posicionais (`(termo, similarity)`) — corrigido para índice numérico; (3) colchete duplicado (erro de sintaxe) introduzido durante uma dessas edições; (4) retornava uma `str` solta em `rag_response`, quando `State` declara `list[str]` — corrigido envolvendo em lista (`[rag_term]`). Levantou por conta própria a ideia de deixar a LLM decidir `top_k` dinamicamente; avaliado como legítimo mas prematuro (exigiria campo novo no `State`, e `vector_store_mock` só tem 3 termos fixos hoje) — registrado como melhoria futura, não implementado. Docstring corrigida para português a pedido explícito do aluno ("arruma pra mim, objetivamente").

**`call_logs_node` completo e validado em execução real (2026-08-24) — primeira vez que client e server MCP reais rodam juntos no projeto.** Decisão de arquitetura (guiada por pergunta, não imposta): reutilizar o servidor MCP do Dia 2 como **processo separado** via `stdio_client`/`Client` do SDK (`mcp.client`), em vez do atalho in-process que o próprio SDK oferece (`Client(mcp_server_instance)`, visto no docstring) — decisão do aluno, justificando que o objetivo declarado da Semana 1/Dia 2 foi treinar a mecânica real do protocolo, e o atalho in-process jogaria isso fora. Também motivado por: `query_logs` não pode ser chamada como função Python solta (usa `ctx.request_context.lifespan_context.pool`, e `ctx` só existe dentro de uma sessão MCP real — chamar sem client faria `None.request_context` estourar, análogo a `NullReferenceException`).

Depuração real (sequência de bugs, todos corrigidos pelo aluno sob pergunta, incluindo dois erros de execução reais com traceback):
1. Import trocado `from multiprocessing.connection import Client` (nome colidindo com stdlib) → corrigido para `from mcp.client import Client` + `from mcp.client.stdio import StdioServerParameters, stdio_client`.
2. Confundiu o `Pool` do Postgres (responsabilidade do *servidor*, já existente em `mcp_server_provider.py`) com a conexão do *client* ao processo do servidor — identificou sozinho, sob pergunta, que o client só consome o serviço, não gerencia a infra do servidor.
3. Chamou `query_logs(conn)` direto de novo (mesmo padrão descartado antes) em vez de `conn.call_tool("query_logs", {...})` — corrigido após lembrete do método correto (recall factual, não dedutível).
4. **Erro de execução real:** `TypeError: 'tuple' object does not support the asynchronous context manager protocol` — código fazia `async with stdio_client(params) as transport` (abrindo o transporte) e depois passava a tupla já aberta pra `Client(transport)`, que tenta abrir ele mesmo por dentro. Aluno interpretou a mensagem de erro corretamente (com guia) e concluiu que `Client` espera o context manager **fechado**, não a tupla já aberta — mentor aplicou a correção a pedido explícito do aluno ("implemente você"), só 1 `async with` (o do `Client`), sem abrir `stdio_client` manualmente.
5. **Erro de infraestrutura real:** container Postgres (`mcp-logs-db`) não estava rodando — servidor MCP crashava no próprio `lifespan` ao tentar `asyncpg.create_pool`, e a sessão do client caía com "Connection closed". Resolvido subindo o container.
6. **Bug de framing real, conectado à lição do Dia 2:** `mcp_server_provider.py.lifespan()` tinha vários `print(...)` de debug escritos em stdout — no mesmo canal usado pro JSON-RPC newline-delimited. Isso quebrava o parsing no client (`Failed to parse JSONRPC message`). Aluno reconheceu sozinho, ao ser lembrado da regra de framing do Dia 2, que linhas de debug em stdout violam a regra "uma mensagem JSON por linha", e removeu os prints.
7. `resultado.structured_content` veio como `{"result": [...]}` (camada extra de aninhamento da tool `query_logs`, que devolve `list[dict]` mas o SDK embrulha em `{"result": ...}`) — aluno identificou a divergência com o tipo declarado em `State` (`list[dict]`) e corrigiu pra `resultado.structured_content["result"]`.

Teste isolado criado em `entrypoints/logs_node_demo.py` (mentor escreveu a pedido explícito do aluno, "tá tarde, faz pra mim") — roda `call_logs_node` com um `State` de teste via `asyncio.run`, imprime o resultado. Rodado várias vezes ao vivo durante a depuração; resultado final: 10 logs reais do Postgres retornados corretamente em `related_logs`. Caveat cosmético não resolvido: caracteres acentuados aparecem como `�` no terminal (provavelmente encoding de exibição do console Windows, não confirmado se é só isso).

**Retomar por:** escrever os nós `A` (entrada/decisão + roteamento condicional) e `D` (saída) em `orchestration/nodes.py`, depois a função de aresta condicional e a montagem do `StateGraph` (arquivo ainda não decidido — provavelmente `orchestration/graph.py`, mesma lógica de separação nós vs. wiring já usada para decidir `nodes.py`). Opcional: investigar o caveat de encoding acima.

### Semana 1 — Dia 3: LCEL — progresso desta sessão (2026-08-11, retomado em 2026-08-19)

| Tarefa do plano | Status |
|---|---|
| Sintaxe pipe (`Prompt \| Model \| Parser`) | **Concluído (conceitual + prática)** — conceitual via analogia com bitwise OR, `__or__`, Middleware Pipeline .NET (11/08); prática em 19/08 com `entrypoints/lcel_demo.py` rodando de ponta a ponta |
| Protocolo Runnable | **Conceitual concluído** — aluno propôs sozinho um contrato genérico `IRunnable<TIn, TOut>` (análogo a `IRequestHandler<TRequest,TResponse>` do MediatR) e deduziu a regra de compatibilidade `TOut` de um componente = `TIn` do próximo |
| `.invoke()` / `.batch()` / `.stream()` | **Todos os três exercitados na prática** em 19/08 — `entrypoints/lcel_invoke_demo.py`, `lcel_batch_demo.py`, `lcel_stream_demo.py`, todos rodando de ponta a ponta com a chain RAG-augmented |
| Prática real (rodar chain nos 3 modos, comparar latência) | **Quase completo** — os 3 modos rodados e validados; falta só o registro formal comparando latência percebida (não feito ainda) |
| Teste `pytest` do schema do parser | **Não iniciado** |

**`entrypoints/lcel_demo.py` (novo, 2026-08-19) — chain RAG-augmented funcional, validada em execução real:**
busca semântica primeiro (`rag.rag_search.search()`, reaproveitando o RAG do Dia 1 — embedding da pergunta do usuário + busca top-1 no `vector_store_mock`), depois monta `ChatPromptTemplate` com o termo técnico resolvido + a pergunta original do usuário como duas lacunas, compõe `prompt | model (ChatOpenAI gpt-4o-mini) | StrOutputParser()`, e roda `.invoke(dict)`. Decisão de design do aluno: a busca RAG é sempre executada antes da chain (sem tool calling) — ele mesmo identificou, corrigindo a própria formulação inicial do prompt ("buscar na nossa base"), que RAG clássico é busca-antes-de-gerar, não a LLM decidindo chamar uma ferramenta (isso é Semana 2). Bugs próprios corrigidos pelo aluno durante a sessão, guiado por perguntas: import errado (`langchain_core.prompt_values` em vez de `langchain_core.prompts`), self-reference incorreta dentro da própria função `rag_search` (`rag_search.search_for_embedding(...)` chamando a si mesma como se fosse o módulo — renomeou a função pra `search` e resolveu), e `.invoke()` recebendo uma lista `[{...}]` em vez de um dict direto (confundiu com o formato esperado por `.batch()`).

Ver `004-knowledge_gaps.md` para os déficits de conhecimento revelados durante essas pontes de analogia.

---

## 1. Progresso por etapa do plano

Referência: `002-study_script.md`.

### Semana 1 — Dia 1: RAG "Do Zero" e Python Performance

| Tarefa do plano | Status |
|---|---|
| Instalar `openai`, `numpy`, `pytest`, `python-dotenv` via `uv add` | **Parcial** — `pytest` não foi instalado |
| Embeddings de termos de arquitetura | **Concluído** |
| Busca vetorial manual (similaridade de cosseno em numpy) | **Concluído** |
| Teste `pytest` validando a similaridade de cosseno | **Não iniciado** |
| Desafio de recuperação: achar "Retry Pattern" a partir de query em português | **Concluído** |
| Registrar em 3-4 linhas quando trocar a busca manual por `pgvector`/`Chroma` | **Não iniciado** |

**Critério de pronto do plano:** "o teste `pytest` passa e a busca manual retorna corretamente Retry Pattern".
→ A segunda metade foi atingida; a primeira **não**. O Dia 1 não está formalmente fechado.

### Semana 1 — Dia 2: Implementação Técnica de MCP

Fase atual: **fundamentação conceitual, ainda sem código.** Nenhuma tarefa do checklist do plano (`002-study_script.md`) foi iniciada — nem `uv add` do SDK, nem o servidor em si.

Sequência socrática percorrida nesta sessão (2026-08-08), cada etapa com conclusão do próprio aluno:

1. MCP não é um contrato lido uma vez por um humano (tipo Swagger) — é consultado em tempo real pela LLM, possivelmente por conversa, com ressalva sobre cache de contexto.
2. Statelessness da chamada de tool (servidor) ≠ statefulness da orquestração (agente).
3. Sessão/conexão deve ser reaproveitada, não recriada por chamada — por analogia com o problema do `HttpClient` em .NET e a solução via `IHttpClientFactory`. Esse componente é o **MCP client**, que abre a sessão via handshake `initialize` e mantém viva pela duração da conversa/processo.
4. Correção da hipótese inicial "MCP ~ REST Web API" para o modelo correto: **RPC**.
5. Reconstrução guiada da estrutura do **JSON-RPC 2.0** a partir do zero: `method`/`params` (RPC), `id` (correlation ID/GUID, por analogia com sistemas distribuídos), convergência para `{id, result}` em vez de ecoar dados que o client já mantém localmente, e objeto de `error` separado para falhas.

Sequência socrática adicional (2026-08-11), fechando a questão de transporte:

6. Concluiu que o client inicia o processo do servidor localmente (não é serviço de rede tradicional), pela lógica de estarem na mesma máquina.
7. Reconheceu, guiado por `Console.WriteLine`, o conceito de streams padrão (stdin/stdout/stderr) e que o terminal é só o destino *padrão*, redirecionável.
8. Deduziu que redirecionar stdout do filho → stdin do pai (e vice-versa) é o mesmo mecanismo do pipe `|` do shell — conectou os dois sozinho.
9. Identificado o problema de *framing* (onde uma mensagem termina no fluxo contínuo de bytes) via analogia com `Console.ReadLine()` e o caractere `\n` (Enter).
10. **Generalizou sozinho** a partir do caso concreto (`\n`) para uma regra abstrata de delimitação: "a mensagem nunca pode conter o caractere X; X separa as mensagens" — e aplicou ao caso do MCP como newline-delimited JSON (uma mensagem por linha). Isso é literalmente como o *stdio transport* do MCP funciona.

**Ponto de retomada exato:** transporte via stdio fechado conceitualmente (processo filho local + streams redirecionados + newline-delimited JSON). Próximo passo do checklist do plano: `uv add` do SDK do MCP e começar a escrever o servidor funcional.

---

## 2. O que existe de fato no código

**Reorganizado em 2026-08-19** (sessão de retomada do Dia 3) — de arquivos soltos em `src/` para pacotes por responsabilidade:

```
src/
  environment_setting.py         # load_dotenv + validação fail-fast das chaves (fica na raiz, cross-cutting)
  entrypoints/                   # scripts executáveis
    __init__.py
    rag_demo.py                  # renomeado de main.py — carrega env, gera embedding da query, busca top-k
    logs_query_mcp_demo.py       # renomeado de logs_query_mcp_starter.py — mcp.run()
  rag/                           # tudo relacionado a embeddings/busca vetorial
    __init__.py
    openai_embedding_service_client.py   # renomeado de openai_service_client.py — só faz embeddings (evita colisão de sentido com "Model" do LCEL)
    vector_store_mock.py         # dict {termo -> embedding} para 3 termos fixos
    rag_search.py                # renomeado de rag.py (colidia com o nome do próprio pacote `rag/`) — cosine_similarity + search_for_embedding
  mcp_server/                    # infra/wiring do protocolo MCP
    __init__.py
    context_lifespan.py
    mcp_server_provider.py
    logs_mcp.py
```

**Decisão de nome — `mcp_server/` em vez de `mcp/`:** a sugestão inicial do mentor (`mcp/`) foi um erro — colidia com o nome do pacote **instalado** via `uv add mcp` (o SDK do protocolo). Descoberta em conjunto: sem `__init__.py` a pasta local não sombreava o pacote real (vira namespace package, Python continua procurando e acha o pacote de verdade em site-packages); mas assim que a pasta ganhasse `__init__.py` — necessário pra virar pacote de verdade — ela passaria a vencer a busca em `sys.path` (que começa pelo diretório de trabalho) e **sombrearia o SDK real**, quebrando todo `from mcp.server.mcpserver import ...` dentro dos próprios arquivos. Renomeado para `mcp_server/` (nome diferente o suficiente pra não colidir).

**Correção de imports (2026-08-19):** todos os imports cruzados entre pastas foram ajustados — relativos (`from .modulo import x`) entre módulos do mesmo pacote, absolutos (`from rag.modulo import x` / `from mcp_server.modulo import x`) entre pacotes diferentes. `environment_setting` continua importável sem prefixo de qualquer lugar (módulo solto na raiz de `src/`).

**Mudança de forma de executar:** rodar o `.py` direto (`uv run script.py`) não funciona mais — só a pasta do próprio script entra no `sys.path`, não `src/` inteira. Os entrypoints agora precisam ser executados como módulo, com `src/` como cwd: `uv run python -m entrypoints.rag_demo` / `uv run python -m entrypoints.logs_query_mcp_demo`.

**Fluxo validado end-to-end (rerodado em 2026-08-19 após a reorganização):** `uv run python -m entrypoints.rag_demo` — a query `"estratégias de resiliência em microserviços"` retorna corretamente `"Padrão de Retentativa"` como termo mais similar entre `["Circuit Breaker", "Padrão de Retentativa", "Sagas"]`. `mcp_server.logs_mcp` importa sem erro (cadeia de import verificada; `mcp.run()` em si não foi reexecutado nesta sessão pra não bloquear em stdio).

### Detalhes de implementação já discutidos e resolvidos

- `cosine_similarity` calcula `dot(a,b) / (norm(a) * norm(b))` e **retorna `0.0` quando qualquer norma é zero** — guarda contra divisão por zero.
- `search_for_embedding` monta uma **lista de tuplas `(termo, similarity)`**, ordena por score decrescente e corta em `top_k`.
- A linha de retorno foi refatorada: havia uma list comprehension identidade (`[t for t in sorted(...)]`) que não transformava nada; hoje é `sorted(...)[:top_k]` direto.

---

## 3. Decisões de design tomadas (não repropor sem motivo)

1. **A busca devolve termo + score, não só o termo.**
   Motivo: quem tem contexto para decidir "isso é bom o suficiente?" é o chamador, não a função de busca. Além disso, sem ver os scores reais da base é impossível calibrar um limiar de corte — o valor "certo" depende do modelo de embedding, do idioma e do tamanho do chunk.
   Analogia usada: o repositório devolve os dados; a regra de negócio decide o que fazer com eles.

2. **Lista de tuplas em vez de dicionário `{texto: score}`.**
   Motivo: com o texto como chave, dois chunks de texto idêntico vindos de fontes diferentes se sobrescrevem **silenciosamente** — perde-se um resultado e a procedência, sem erro nenhum.

3. **Separação conceitual entre dois tipos** (ainda não materializada em código):
   - **Chunk** — o que o vector store guarda: `fonte`, `referencia`, `id`, `texto`, `embedding`. Existe independentemente de qualquer pergunta.
   - **Resultado de busca** — Chunk + `similarity`. Só existe em relação a uma query.
   Equivalente .NET: entidade vs. projeção de consulta (a entidade não carrega o `Rank` que só apareceu por causa do `ORDER BY`).

4. **Filtros dinâmicos da tool MCP de `SELECT` (`service_logs`) usam duas listas paralelas (`conditions: list[str]`, `params: list`), não um dicionário.**
   Motivo: mesmo princípio da decisão 2 (Dia 1) — usar um valor vindo de fora (da LLM) como chave de dicionário arrisca colisão e sobrescrita silenciosa de condição, mesmo que rara. As duas listas crescem em conjunto, indexadas por um contador manual que numera os placeholders posicionais (`$1, $2, ...`) do `asyncpg`.
   Contexto: os 4 filtros da tool (período, origem, level, mensagem) são todos **opcionais** — campo ausente = não filtra por ele. Um filtro "obrigatório mas com valor amplo o suficiente pra não filtrar nada" foi descartado por ser equivalente a opcional, só que mais complicado.
   Motivação de performance: montar o `WHERE` só com as condições presentes (em vez do padrão fixo `campo = $N OR $N IS NULL`) evita que o Postgres monte um plano de execução genérico sem uso de índice — o parâmetro dinâmico impede o otimizador de sniffar o valor em tempo de plano.

5. **Conexão com o Postgres via `asyncpg.create_pool()`, não conexão única compartilhada nem `asyncpg.connect()` avulso por chamada.**
   Motivo: confirmado via documentação oficial (`protocol-flow.html` do Postgres — comandos numa mesma conexão são processados sequencialmente, aguardando `ReadyForQuery`) que uma única conexão compartilhada serializaria/travaria chamadas concorrentes da tool MCP. Abrir uma conexão nova (`connect()`) a cada chamada evitaria a serialização, mas pagaria o custo de handshake TCP + autenticação toda vez — custo que o ADO.NET esconde via pooling interno mesmo em `new SqlConnection()` por requisição. `Pool` do `asyncpg` reproduz esse mesmo comportamento (documentação oficial recomenda pool para "server-type applications" com requisições frequentes e curtas): isolamento por chamada (`pool.acquire()`) sem repetir o custo de conexão.

6. **Metadados de origem no texto embeddado são desejáveis, mas não substituem estrutura.**
   Enriquecer o chunk com um cabeçalho tipo `[Fonte: manual X — pág. Y]` antes de gerar o embedding melhora a recuperação. Mas os metadados também devem existir em campos estruturados no retorno — não apenas concatenados na string.

---

## 4. Dívidas técnicas conhecidas (assumidas conscientemente)

| Item | Descrição | Decisão |
|---|---|---|
| Logging | `rag.py` usa `print` dentro do loop, incluindo o embedding inteiro (1536 floats por termo). Não escala. | Adiado pelo aluno — tratar quando o volume doer |
| Testes | Nenhum teste automatizado no projeto; `pytest` não instalado | Pendente do Dia 1 |
| Vector store | `vector_store_mock.py` é um dict em memória com 3 termos; sem chunking, sem persistência, sem metadados | Consciente — parte do exercício "do zero" |
| Nome de variável | `top_tuples` descreve a estrutura, não o significado | Cosmético |
| Imports | ~~`main.py` usa imports sem prefixo de pacote~~ — **resolvido em 2026-08-19** com a reorganização em pacotes (`entrypoints/`, `rag/`, `mcp_server/`) e imports absolutos/relativos corrigidos | Fechado |
| `LANGSMITH_API_KEY` | Exigida em `environment_setting.py` (fail-fast), mas o pacote `langsmith` não é dependência do projeto | Verificar se é intencional |
| Separação DAO vs. exposição MCP | `logs_mcp.py` (renomeado de `logs_dao.py` em 2026-08-18) mistura acesso a dados puro com decorators `@mcp.tool()`/`@mcp.resource()` e `Context` do SDK — não é mais um DAO desacoplado de protocolo | Consciente — aluno decidiu manter fundido por ora; separar em `logs_dao.py` (puro) + arquivo de wiring MCP é opção futura, não descartada |

---

## 5. Divergências entre documentos e realidade

- `pyproject.toml` declara `requires-python = ">=3.14"`. O plano (`002-study_script.md`) e o `CLAUDE.md` mencionam `>=3.12`. A realidade é 3.14 — os documentos é que estão desatualizados.
- O plano prescreve `venv` + `pip`; o projeto usa **`uv`**. Override deliberado do aluno, já registrado em `003-current_environment.md`. Traduzir em tempo real, não alterar os documentos-fonte.

---

## 6. Próximo passo

**Decisão (2026-08-19, fim de sessão):** aluno avançou no mesmo dia até Semana 2/Dia 1 (LangGraph) e pausou por vontade própria logo depois de desenhar (só na conversa, não em código) o `TypedDict` de estado do grafo — ver seção 1, "Semana 2 — Dia 1: LangGraph".

**Retomar a sessão por:** criar `src/orchestration/` (nome decidido em 2026-08-24, ver seção 1) e escrever de verdade a classe `State(TypedDict)` já desenhada (com `NotRequired[...]` nos campos opcionais), depois seguir pro resto do checklist do Dia 1/Semana 2 (nós, bordas condicionais, visualização do grafo). Dívidas mais antigas que continuam em aberto, sem data prevista: `pytest` do parser LCEL (Dia 3), `pytest` da similaridade de cosseno (Dia 1), teste automatizado da tool MCP (Dia 2) — ver seção 1 e seção 4.
