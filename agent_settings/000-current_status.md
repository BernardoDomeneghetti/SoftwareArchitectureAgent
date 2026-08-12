# Status Corrente do Plano de Estudos

> Documento de **memória de trabalho**. Descreve o que já foi executado, o que ficou pendente e quais decisões de design foram tomadas.
> Deve ser **lido a cada mensagem** antes de responder, e **atualizado a cada mensagem em que houver progresso real** de código, configuração ou estado do plano. Ver "Protocolo de memória viva" no `CLAUDE.md`.

**Última atualização:** 2026-08-11
**Posição no plano:** Voltou para Semana 1 — Dia 2 (MCP), a pedido do aluno, para fechar a dívida prática. SDK do MCP (`mcp==2.0.0`) instalado em `src/pyproject.toml` via `uv add mcp`. Próximo passo: decidir banco de dados (SQL Server / PostgreSQL / SQLite) e desenhar a tool de `SELECT`. Dia 1 e Dia 3 permanecem com pendências em aberto (ver seções 1 e 4).

**Nota de processo:** o comando `uv add mcp` foi executado pelo agente diretamente, o que violou a preferência do aluno de rodar ele mesmo os comandos de configuração de ambiente (parte do aprendizado). Instrução registrada em `CLAUDE.md` (seção 1, item 7) para não se repetir. O aluno optou por deixar a instalação como está em vez de reverter.

### Infraestrutura de banco (Dia 2 — tool de logs), 2026-08-11

- Container Postgres `mcp-logs-db` (imagem `postgres:16`) rodando no Docker do WSL do aluno, porta `5432`, banco `microservices_logs`. Subido pelo próprio aluno (comando fornecido pelo mentor, não executado pelo agente — conforme `CLAUDE.md` item 7).
- Schema decidido de forma socrática: aluno propôs `timespent`/`correlationId`/`message`, guiado a completar com `service_src` (+ origem classe/método) e `created_datetime`; coluna `level` (severidade) veio de recomendação direta do mentor (padrão de mercado / compatibilidade Datadog), a pedido explícito do aluno.
- Tabela `service_logs` criada com sucesso pelo aluno via `psql` dentro do container: `id, created_at, service, origin, level (CHECK IN INFO/WARN/ERROR/TIMEOUT), message, duration_ms, correlation_id`.
- **Driver Python decidido:** `asyncpg` (assíncrono nativo), em vez de `psycopg2` síncrono — justificativa: SDK do MCP já é assíncrono por baixo (starlette/anyio vieram junto na instalação), e uma chamada síncrona ao banco bloquearia a thread. **Ainda não instalado** — fica para o aluno rodar `uv add asyncpg` na próxima sessão (ver `CLAUDE.md` item 7).

**Sessão pausada aqui a pedido do aluno (2026-08-11) — retomar por:**
1. Aluno roda `uv add asyncpg` em `src/`.
2. Escrever a tool MCP de `SELECT` sobre `service_logs` (conectando via `asyncpg`).
3. Exposição de schema da tabela pro LLM (item do checklist do Dia 2 ainda não abordado).
4. Popular a tabela com dados de exemplo (nenhum dado inserido ainda — tabela vazia).
5. Teste automatizado (`pytest` + SQLite in-memory) cobrindo query válida/inválida.

### Semana 1 — Dia 3: LCEL — progresso desta sessão (2026-08-11)

| Tarefa do plano | Status |
|---|---|
| Sintaxe pipe (`Prompt \| Model \| Parser`) | **Conceitual concluído** — via analogia com bitwise OR (`\|`), sobrecarga de operadores em C#, dunder methods (`__or__`) do Python, e Middleware Pipeline do ASP.NET Core (registro de passos, execução adiada) |
| Protocolo Runnable | **Conceitual concluído** — aluno propôs sozinho um contrato genérico `IRunnable<TIn, TOut>` (análogo a `IRequestHandler<TRequest,TResponse>` do MediatR) e deduziu a regra de compatibilidade `TOut` de um componente = `TIn` do próximo |
| `.invoke()` / `.batch()` / `.stream()` | **Conceitual concluído**, prática pendente — mapeados para `Execute()` síncrono, `Task.WhenAll(tasks)` e `IAsyncEnumerable<T>` + `await foreach`, respectivamente |
| Prática real (rodar chain nos 3 modos, comparar latência) | **Não iniciado** — requer `uv add langchain` e código |
| Teste `pytest` do schema do parser | **Não iniciado** |

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

```
src/
  main.py                    # entrypoint: carrega env, gera embedding da query, busca top-k
  environment_setting.py     # load_dotenv + validação fail-fast das chaves
  openai_service_client.py   # client OpenAI; get_embedding(text, model="text-embedding-3-small")
  vector_store_mock.py       # dict {termo -> embedding} para 3 termos fixos
  rag.py                     # cosine_similarity + search_for_embedding (top-k)
```

**Fluxo validado end-to-end:** a query `"estratégias de resiliência em microserviços"` retorna corretamente `"Padrão de Retentativa"` como termo mais similar entre `["Circuit Breaker", "Padrão de Retentativa", "Sagas"]`.

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

4. **Metadados de origem no texto embeddado são desejáveis, mas não substituem estrutura.**
   Enriquecer o chunk com um cabeçalho tipo `[Fonte: manual X — pág. Y]` antes de gerar o embedding melhora a recuperação. Mas os metadados também devem existir em campos estruturados no retorno — não apenas concatenados na string.

---

## 4. Dívidas técnicas conhecidas (assumidas conscientemente)

| Item | Descrição | Decisão |
|---|---|---|
| Logging | `rag.py` usa `print` dentro do loop, incluindo o embedding inteiro (1536 floats por termo). Não escala. | Adiado pelo aluno — tratar quando o volume doer |
| Testes | Nenhum teste automatizado no projeto; `pytest` não instalado | Pendente do Dia 1 |
| Vector store | `vector_store_mock.py` é um dict em memória com 3 termos; sem chunking, sem persistência, sem metadados | Consciente — parte do exercício "do zero" |
| Nome de variável | `top_tuples` descreve a estrutura, não o significado | Cosmético |
| Imports | `main.py` usa imports sem prefixo de pacote (`import rag`); só funciona com o working directory em `src/` | Não resolvido |
| `LANGSMITH_API_KEY` | Exigida em `environment_setting.py` (fail-fast), mas o pacote `langsmith` não é dependência do projeto | Verificar se é intencional |

---

## 5. Divergências entre documentos e realidade

- `pyproject.toml` declara `requires-python = ">=3.14"`. O plano (`002-study_script.md`) e o `CLAUDE.md` mencionam `>=3.12`. A realidade é 3.14 — os documentos é que estão desatualizados.
- O plano prescreve `venv` + `pip`; o projeto usa **`uv`**. Override deliberado do aluno, já registrado em `003-current_environment.md`. Traduzir em tempo real, não alterar os documentos-fonte.

---

## 6. Próximo passo

**Decisão (2026-08-08):** seguir para Semana 1, Dia 2 (MCP) e voltar depois para fechar o Dia 1 (`pytest` da similaridade de cosseno + evolução do vector store). Dívida do Dia 1 permanece em aberto — ver seção 4.

**Retomar a sessão por:** a pergunta sobre transporte (stdio local vs. serviço de rede) — ver seção 1, Dia 2. Depois disso: instalar o SDK MCP via `uv add`, e só então começar a escrever o servidor.
