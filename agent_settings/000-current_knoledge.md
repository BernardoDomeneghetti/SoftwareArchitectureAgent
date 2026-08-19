# Resumo do Perfil e Objetivos do Projeto

> **Memória viva.** Deve ser lido a cada mensagem e atualizado sempre que o aluno **demonstrar** domínio de um tópico — não quando apenas concordar com uma explicação. Ver "Protocolo de memória viva" no `CLAUDE.md`.

## 1. Conhecimentos Possuídos

- Desenvolvedor .NET com experiência em sistemas distribuídos, microserviços, Kubernetes, Docker, redes e APIs.
- Domínio de bancos de dados relacionais e conhecimento intermediário em tecnologias NoSQL.
- Base em arquitetura de software.

## 2. Conhecimentos Necessários para o Tema e Objetivo (Done)

- **Fundamentos de Frameworks**: compreensão teórica sobre o propósito e utilidade do LangChain e do LangGraph.
- **RAG (Retrieval-Augmented Generation)**: entendimento de como funciona e para que serve, com capacidade de configurar o ambiente e realizar implementações utilizando as abstrações nativas do LangChain.
- **Conceitos de Protocolos**: entendimento conceitual inicial sobre o MCP (Model Context Protocol).

## 3. Conhecimentos Necessários para o Tema e Objetivo (Pendente)

- **Domínio Prático Profundo**: necessidade de dominar as funcionalidades do LangChain e LangGraph para uso efetivo no dia a dia.
- **RAG de Baixo Nível — etapas restantes**: chunking, enriquecimento de chunks com metadados estruturados, persistência vetorial e critérios para migrar da busca manual para `pgvector`/`Chroma`. *(A parte de embeddings + similaridade + top-k já foi coberta — ver seção 4.)*
- **Execução Técnica de MCP**: evoluir do entendimento superficial para a capacidade real de implementação do protocolo.
- **Linguagens Específicas**: transição ou aquisição de proficiência em Python ou Node.js, conforme exigido pelos requisitos da vaga de Engenheiro de IA.
- **Testes em Python**: `pytest` ainda não instalado nem exercitado. Vindo de .NET, o aluno conhece o conceito — falta o ferramental.
- **Logging estruturado em Python**: hoje usa `print`. Tópico adiado deliberadamente.

---

## 4. Aprendizados demonstrados em sessão

> Registrados apenas com evidência: o aluno deduziu a consequência, achou sozinho a falha no próprio raciocínio, ou aplicou o conceito em contexto novo.

### 2026-08-08 — Semana 1, Dia 1

**Estruturas de dados do Python**

- Distingue `[]` (list), `{}` (dict) e `()` (tuple). Chegou em "tupla" sozinho via analogia com `ValueTuple` do C#. *Evidência: corrigiu a própria classificação errada de `similarities` quando confrontado com a linha `similarities = []`.*
- Entende desempacotamento em list comprehension (`for termo, _ in ...`) e o papel do `_` como descarte.
- Reconhece list comprehension identidade como código sem efeito. *Evidência: comparou as duas versões da linha e concluiu "nada, simplificou".*

**RAG de baixo nível**

- Implementou similaridade de cosseno manualmente em numpy, incluindo guarda contra norma zero.
- Implementou busca top-k com ordenação por score.
- Deduziu que usar o texto do chunk como chave de dicionário causa **sobrescrita silenciosa** de chunks idênticos. *Evidência: previu o comportamento antes de ser dito.*
- Argumentou corretamente que a deduplicação, ocorrendo antes do corte `top_k`, não reduz a quantidade de resultados — refinou o próprio raciocínio sob contra-exemplo em vez de aceitar a objeção de imediato.
- Chegou por conta própria à ideia de enriquecer o chunk com cabeçalho de procedência (`[Fonte: manual X — pág. Y]`) antes de gerar o embedding.
- Rejeitou concatenar metadados em string única quando confrontado com a analogia de DTO em C#; propôs objeto estruturado com `Fonte`, `Referencia`, `Index` (hash), `text`, `similarity`.
- **Distinguiu corretamente entidade de projeção de consulta**, e corrigiu o mentor quando este confundiu o objeto armazenado no vector store com o objeto resultante da busca. *Melhor evidência da sessão: pushback tecnicamente correto.*
- Convergiu para a separação entre **recuperar** e **decidir o que é bom o suficiente**: a busca devolve os scores, a política de corte é do chamador.

**Ambiente**

- `uv` como gerenciador de pacotes: `uv init`, `uv add`, mapeamento para `.csproj`/`packages.lock.json`.
- Gestão de segredos com `python-dotenv` + `.env` + validação fail-fast.

### 2026-08-08 — Semana 1, Dia 2 (em andamento)

**MCP — introdução conceitual**

- Identificou Swagger/OpenAPI como o mecanismo pelo qual uma Web API .NET se autodescreve para consumidores.
- Deduziu, sem ser dito, que no caso do MCP quem consome essa "documentação" é a própria LLM, e que a consulta tende a ser **em tempo real por conversa**, não uma leitura única em tempo de desenvolvimento como um dev lendo Swagger — aplicando a analogia Web API a um contexto novo. Já matizou com a hipótese de cache de contexto.
- Distinguiu sozinho **statelessness da chamada de tool individual** (do lado do servidor) de **statefulness da orquestração** (do lado do contexto do agente) — separação que não é óbvia e não foi sugerida diretamente.
- Conectou o dilema "abrir conexão nova por chamada vs. reaproveitar sessão" ao problema conhecido do `HttpClient` em .NET, e concluiu sozinho — a partir da solução real desse problema (`IHttpClientFactory`) — que faz sentido **terceirizar o gerenciamento da conexão/sessão para um componente especializado** em vez de gerenciar manualmente. *Evidência: transferência de um padrão de solução .NET para um problema novo em MCP, sem que o mentor apontasse a analogia.*
- Corrigiu sozinho sua própria hipótese inicial (MCP ~ REST Web API) para o modelo correto (RPC), ao reconhecer que "chamar uma tool pelo nome com parâmetros" é uma chamada de função remota, não uma operação sobre recurso.
- Reconstruiu, por dedução guiada, a estrutura essencial do **JSON-RPC** sem conhecer o nome do protocolo: chegou a `method`/`params` via RPC, chegou ao **correlation ID** citando GUIDs de sistemas distribuídos, e — aplicando a mesma lógica duas vezes (para `params` e depois para "origem") — concluiu sozinho que a resposta não precisa ecoar dados que o client já mantém localmente (ex: `Dictionary<Guid, ...>`), convergindo para `{id, result}` + objeto de erro separado. *Evidência mais forte: auto-aplicação do próprio argumento de redundância a um segundo campo, sem que o mentor precisasse repetir o raciocínio.*

### 2026-08-11 — Semana 1, Dia 2 (continuação — transporte stdio)

- Deduziu que, para processos na mesma máquina, o transporte tenderia a ser local em vez de rede tradicional.
- Conectou o mecanismo de redirecionamento de stdout/stdin de processo pai/filho ao pipe `|` do shell **por conta própria**, reconhecendo-os como o mesmo primitivo do SO.
- Identificou o problema de framing (delimitação de mensagens num stream contínuo de bytes) e, a partir do caso concreto de `\n`/Enter, **generalizou para uma regra abstrata**: um caractere delimitador só funciona se for proibido dentro do conteúdo da mensagem. Aplicou a regra corretamente ao MCP como "uma mensagem JSON por linha". *Evidência: generalização de um exemplo concreto para uma regra reutilizável, sem que o mentor enunciasse a regra abstrata primeiro.*

### 2026-08-18 — Semana 1, Dia 2 (continuação — `context_lifespan.py` e `mcp_server_provider.py`)

- Deduziu sozinho, a partir do padrão já usado por ele mesmo (`async def`, não `defasync`), a sintaxe `async with` como versão assíncrona de `with`, antes de qualquer confirmação — acertou primeiro a ordem das palavras, depois o espaçamento, ambos autocorrigidos sob pergunta.
- Diante do conceito novo de `yield`/generator (auto-declarado "totalmente novo", registrado em `004-knowledge_gaps.md`), absorveu a explicação e aplicou corretamente ao identificar que a linha **após** o `yield` (fechamento do pool) corresponde ao `Dispose()` do `IDisposable` — não a linha antes.
- Propôs a analogia `dataclass` ~ `struct` de C#; ao ser questionado sobre semântica de value type vs. reference type, **autocorrigiu** para "classe comum" (reference type), reconhecendo a diferença sem que o mentor precisasse dar a resposta.
- Aplicou a convenção PEP 8 (`snake_case` para arquivos/funções, `PascalCase` para classes) corretamente em três contextos consecutivos depois de ser questionado (nome de arquivo `ContextLifespan.py` → `context_lifespan.py`; nome de classe `lifespan_context` → `LifespanContext`; nome de função `Get` → candidato a renomear).
- Deduziu sozinho a distinção entre função-factory (verbos `create_`/`build_`/`make_`, devolve objeto novo) e função-hook-de-ciclo-de-vida (nomeada igual ao parâmetro que a recebe), articulando que a função "encapsula o acesso ao objeto com um `with`/`using` por trás dos panos" — motivo pelo qual `lifespan` (não `get_lifespan`) é o nome correto.
- **Validação experimental do transporte stdio (Dia 2):** rodou `logs_query_mcp_starter.py` pela primeira vez e observou exatamente o comportamento previsto meses antes só na teoria (processo trava em `mcp.run()` esperando stdio, sem client conectado) — confirma que o modelo mental construído por dedução (sem nunca ter rodado o código) estava correto na prática.

### 2026-08-18 — Semana 1, Dia 2 (continuação — Resources do MCP, dados de exemplo, exposição de schema)

- Diante da distinção nova (Tool vs. Resource no MCP), propôs sozinho uma regra inicial ("Resource = leitura, Tool = mutação/ação"); confrontado com a contradição de que `query_logs` (leitura pura, um `SELECT`) já era uma Tool, **refinou a própria regra** para o critério correto — presença ou ausência de parâmetros dinâmicos que a LLM decide/compõe — sem que o mentor entregasse a resposta pronta.
- Verificou os tipos reais das colunas de `service_logs` via `\d service_logs` no `psql`, em vez de aceitar o chute inicial (`id: UUID`) sem checar — reconheceu a lacuna quando questionado ("nunca documentaram se é UUID, SERIAL ou outro tipo") e foi buscar o dado real.
- Identificou e resolveu, ao ser confrontado, uma ambiguidade de nomenclatura própria: o parâmetro `origin` da tool `query_logs` filtra a coluna `service`, não a coluna `origin` do banco — reescreveu a descrição da coluna `origin` na resource de schema pra desambiguar essa colisão de nomes antes que confundisse uma LLM lendo os dois artefatos juntos.

### 2026-08-13 — Semana 1, Dia 2 (continuação — driver `asyncpg` e design da tool de `SELECT`)

- Reconstruiu a analogia .NET entre a camada genérica ADO.NET (`IDbConnection`/`IDbCommand`) e a camada de provider específico por SGBD (`Npgsql`, `Microsoft.Data.SqlClient`); autocorrigiu, ao ser questionado, a hipótese inicial de que a diferença entre `asyncpg` e o provider .NET seria "específico vs. genérico" — reconheceu que ambos são específicos por SGBD, e que a genericidade está numa camada acima (a interface ADO.NET), inexistente de forma equivalente no lado async do Python.
- Projetou os parâmetros da tool MCP de `SELECT` sobre `service_logs` (período, origem, level, mensagem) e concluiu sozinho, sob questionamento, que todos deveriam ser **opcionais** — percebeu a contradição em tratar um campo como "obrigatório, mas preenchível com um valor amplo o suficiente pra não filtrar nada", equivalente a simplesmente torná-lo opcional.
- A partir do padrão `WHERE (campo = $1 OR $1 IS NULL)` (que already usava com Dapper/.NET), **deduziu sem ser dito** a causa raiz do problema de performance: o parâmetro sendo dinâmico (valor desconhecido em tempo de plano) força o otimizador do banco a montar um plano de execução genérico, incapaz de usar índice na coluna filtrada. *Evidência: foi além de "o OR mata a performance" (intuição correta mas rasa) para explicar o mecanismo exato quando questionado sobre a diferença entre "OR trava índice sempre" vs. "parâmetro dinâmico força plano genérico".*
- Propôs substituir as duas listas paralelas (condições SQL + valores) por um dicionário `valor -> fragmento SQL`. Ao ser questionado com um cenário de colisão, **transferiu sozinho** a lição do Dia 1 (usar texto de chunk como chave de dicionário causa sobrescrita silenciosa) para esse contexto novo — reconheceu que usar um valor vindo de fora (da LLM) como chave tem o mesmo risco, independente da colisão ser rara, e voltou por conta própria para a estrutura de duas listas. *Evidência: aplicação de um princípio aprendido em contexto totalmente diferente (RAG/vector store) a um problema novo (montagem dinâmica de SQL), sem que o mentor enunciasse o princípio de novo.*
- Previu corretamente, antes de qualquer confirmação, que o Postgres serializa comandos dentro de uma única conexão (chamou de "fila"). Diante do dilema entre conexão única compartilhada, conexão nova a cada chamada, e `Pool`, inicialmente achou que "conexão nova por chamada" seria mais simples que um `Pool`. Ao lembrar que o **ADO.NET já faz pooling de conexões físicas por baixo dos panos** mesmo quando o código escreve `new SqlConnection()` a cada requisição, **sintetizou sozinho** a conclusão correta: o `Pool` não é uma alternativa à ideia de "conexão isolada por chamada", é o mecanismo que entrega exatamente isso — sem pagar o custo de handshake TCP/autenticação repetido. *Evidência: reconciliou duas ideias aparentemente conflitantes (isolamento vs. reuso) numa síntese própria, a partir de um comportamento do ADO.NET que ele já usava sem saber que existia.*

### 2026-08-19 — Semana 1, Dia 3 (retomada — pacotes do ecossistema LangChain)

- Transferiu sozinho, sem o mentor enunciar de novo, a distinção genérico/específico já usada para `asyncpg`/ADO.NET (sessão de 2026-08-13) para o ecossistema LangChain: concluiu que existe um pacote "core" genérico (motor do `Runnable`/pipe) separado de pacotes "conectores" específicos por provider (ex.: OpenAI) — antes de qualquer nome de pacote real ser mencionado. *Evidência: aplicação do mesmo princípio estrutural a um domínio novo, por conta própria.*
- Deduziu o nome real do pacote genérico (`langchain-core`) a partir da convenção `framework-especialização` que ele mesmo já tinha usado pra acertar `langchain-openai` — quando confrontado com a diferença entre "langchain" (guarda-chuva) e o pacote específico do "motor" (Runnable/prompts/parsers), chegou ao sufixo `-core` sem o nome ser dito. *Evidência: aplicação de um padrão de nomenclatura já validado a um caso novo, sem repetição da regra pelo mentor.*
- Ao escrever o primeiro prompt da chain LCEL pedindo pra LLM "buscar o termo na nossa base", **identificou sozinho a própria contradição** ao ser questionado se a LLM tem acesso a essa "base" dentro de um pipe puro `Prompt \| Model \| Parser` (sem RAG integrado) — corrigiu a própria formulação, reconhecendo que RAG "clássico" significa *buscar antes* e injetar o resultado como contexto no prompt, não a LLM pedindo/decidindo buscar (isso seria tool calling, padrão diferente, visto no Dia 2/MCP). *Evidência: autocorreção de uma confusão conceitual real entre dois padrões de arquitetura (RAG por injeção de contexto vs. tool calling), sem o mentor entregar a distinção pronta — só apontou a pergunta que expôs a contradição.*
- Construiu `entrypoints/lcel_invoke_demo.py` (então `lcel_demo.py`) de ponta a ponta com uma chain real (`prompt | model | parser`) integrando a busca semântica do Dia 1, e depurou sozinho, guiado só por perguntas/tracebacks reais (nunca pela correção pronta), três bugs próprios: (1) import de `ChatPromptTemplate` do módulo errado (`prompt_values` em vez de `prompts`) — aplicou o mesmo hábito já estabelecido no Dia 2 de checar `site-packages` em vez de confiar de cabeça; (2) dentro da função `rag_search`, escreveu `rag_search.search_for_embedding(...)` tentando qualificar uma função-irmã do mesmo arquivo como se precisasse de prefixo — reconheceu a auto-referência errada e resolveu renomeando a função pra `search`; (3) passou uma lista `[{...}]` pra `.invoke()` em vez de um dict direto — **conectou sozinho ao erro com a distinção `.invoke()` vs. `.batch()` que ele mesmo tinha mapeado em 11/08**, sem o mentor precisar reexplicar a diferença. *Evidência mais forte: usou um conceito abstrato aprendido meses antes, sem executar nada, para diagnosticar um bug concreto na primeira vez que a API realmente rodou.*
- Estendeu a chain pra `.batch()` (`lcel_batch_demo.py`) sozinho: montou o loop que roda a busca RAG por pergunta e monta a lista de dicts, executou, e **corrigiu por conta própria** um bug de escopo de variável (print fora do loop mostrando só o valor da última iteração) movendo o print pra dentro do loop — sem que o mentor precisasse explicar a diferença de escopo `for` entre Python e C#. Também formulou uma hipótese testável antes de rodar (qual pergunta ativaria "Circuit Breaker" vs. "Padrão de Retentativa"), aceitando o resultado empírico quando a intuição inicial não bateu.
- Reconheceu a distinção `.batch()` (múltiplas entradas independentes, um resultado por entrada) vs. uma única resposta combinada, comparando corretamente com `Task.WhenAll` — a mesma analogia que ele mesmo tinha proposto em 11/08, agora validada rodando de verdade.
- Em `.stream()` (`lcel_stream_demo.py`): cometeu e diagnosticou sozinho, sob pergunta, o erro espelhado do de `.invoke()` (passou a lista de `.batch()` por engano, corrigiu pra um dict só ao ser lembrado que `.stream()` processa uma entrada por vez). Diante do generator não-consumido (`print(response)` mostrando o objeto generator em vez do texto), não soube de imediato o mecanismo de consumo ("não sei"), mas **aplicou corretamente a explicação de generator/`yield`** (aprendida no Dia 2 com o `lifespan` do MCP) ao escrever o `for chunk in response`, e adicionou `flush=True` por conta própria — reconheceu sozinho que a saída em stream precisa ser exibida sem buffer pra ter efeito visual real.

### 2026-08-11 — Semana 1, Dia 3 (LCEL — pipe syntax e Runnable protocol)

- Autocorrigiu a hipótese inicial de que `__or__`/`\|` executaria a chain imediatamente na composição — reconheceu, ao ser questionado sobre a ordem temporal dos eventos, que o operador só **registra** os passos, e a execução real fica para `.invoke()`. *Evidência: identificou sozinho a falha no próprio raciocínio ao ser confrontado com a linha de código real.*
- Propôs, sem receber a resposta pronta, um contrato genérico (`IRunnable<TIn, TOut>` com método único parametrizado, análogo a `IRequestHandler<TRequest,TResponse>`) como solução para heterogeneidade de tipos numa chain — chegando muito perto do nome real do conceito (Runnable protocol) antes de ele ser revelado.
- Deduziu corretamente, a partir do contrato genérico, a regra de compatibilidade de tipos entre componentes encadeáveis (`TOut` de um = `TIn` do próximo).
- Mapeou corretamente `.batch()` do LCEL para o padrão de disparar múltiplas `Task`s e aguardá-las juntas (`Task.WhenAll`), com a lógica certa mesmo errando o nome exato do método.
