# Plano de Estudos: Engenharia de IA com Ecossistema uv (Migração .NET)

## Objetivo Principal

Migrar a senioridade em arquitetura .NET e sistemas distribuídos para Engenharia de IA, dominando RAG de baixo nível, o protocolo MCP e orquestração com LangGraph — sob um fluxo de trabalho moderno, performático e tipado.

## Introdução e Alinhamento Estratégico

Para o desenvolvedor vindo do .NET, a transição para Python costuma esbarrar na fragmentação de ferramentas (pip, venv, poetry, pyenv). Este plano elimina essa fricção adotando o **uv**, escrito em Rust, que unifica o workflow e traz o determinismo já esperado por quem vem de C#:

| Conceito uv | Equivalente .NET |
|---|---|
| `uv.lock` | `packages.lock.json` |
| `pyproject.toml` | `.csproj` |

**Versões de referência do plano** (fixar no `pyproject.toml` para reprodutibilidade):

- Python `>=3.12`
- Modelo LLM de exemplo: `gpt-4o-mini` (ou equivalente — trocar por preferência, mas manter fixo durante todo o plano para comparar resultados de forma justa)

---

## Pré-requisitos (checkpoint antes do Dia 1)

Antes de iniciar, valide fluência nos seguintes pontos de Python — se algum item falhar, reserve 1-2h avulsas para revisão antes de seguir:

- [ ] List/dict comprehensions e generators.
- [ ] `async`/`await` e a diferença para o modelo de threads do .NET.
- [ ] Tipagem com `typing` (`TypedDict`, `Optional`, `Protocol`) como equivalente a interfaces/DTOs.
- [ ] Context managers (`with`) como analogia a `IDisposable`/`using`.

---

## Preparação do Ambiente com uv

O `uv` automatiza o contexto do projeto de forma similar ao `dotnet` CLI — sem instalação global de pacotes nem gestão manual de `.venv`.

- **Inicialização do projeto**: cria a estrutura base e o `pyproject.toml`.
- **Gestão declarativa de dependências**: adicionar bibliotecas resolve a árvore de dependências instantaneamente e gera o lockfile.
- **Sincronização e determinismo**: garante que o ambiente local reflita exatamente o lockfile.
- **Execução de scripts**: `uv run` roda o código no ambiente correto sem ativação manual (`source .venv/bin/activate`).

---

## Semana 1 — Fundamentos de Baixo Nível e Integração de Dados (9h)

### Dia 1 — RAG "Do Zero" e Python Performance (~3h)

Objetivo: desmistificar a recuperação vetorial antes de usar abstrações de alto nível.

- [ ] *(20 min)* Configuração: instalar `openai`, `numpy`, `pytest` e `python-dotenv` via `uv add`.
- [ ] *(45 min)* Embeddings de documentação técnica: função para converter termos de arquitetura ("Circuit Breaker", "Padrão de Retentativa", "Sagas") em vetores numéricos.
- [ ] *(45 min)* Busca vetorial manual: similaridade de cosseno implementada puramente em `numpy`.
- [ ] *(30 min)* Teste automatizado: escrever um teste `pytest` que valida a função de similaridade de cosseno com vetores conhecidos (ex.: vetores idênticos → similaridade 1.0; ortogonais → 0.0).
- [ ] *(30 min)* Desafio de recuperação: buscar em uma lista de strings técnicas e encontrar a definição de "Retry Pattern" ao perguntar sobre "estratégias de resiliência em microserviços" — sem bancos vetoriais prontos.
- [ ] *(10 min)* Comparação com solução gerenciada: registrar em 3-4 linhas quando faria sentido trocar a busca manual por `pgvector` ou `Chroma` (ex.: volume de documentos, necessidade de filtros/metadados, atualização incremental).

**Pronto quando:** o teste `pytest` passa e a busca manual retorna corretamente "Retry Pattern" para a query em português.

### Dia 2 — Implementação Técnica de MCP (Model Context Protocol) (~3h)

Objetivo: transformar experiência em bancos relacionais em ferramentas para o LLM.

- [ ] *(40 min)* Servidor MCP: criar um servidor funcional com o SDK do MCP via `uv`.
- [ ] *(50 min)* Tool de banco de dados: ferramenta que executa `SELECT` em logs de microserviços (SQL Server ou PostgreSQL) para expor métricas ao LLM.
- [ ] *(40 min)* Exposição de schema: configurar o servidor para fornecer metadados das tabelas, permitindo que o LLM entenda o contexto relacional antes de gerar queries.
- [ ] *(30 min)* Teste automatizado: `pytest` cobrindo a tool MCP com um banco de teste (SQLite in-memory é suficiente) validando que uma query válida retorna os dados esperados e uma query inválida retorna erro tratado.

**Pronto quando:** o servidor MCP responde a uma chamada de tool real via cliente de teste (ex.: MCP Inspector) e os testes automatizados passam.

### Dia 3 — Domínio de LCEL (LangChain Expression Language) (~3h)

Objetivo: o LCEL traz para Python a elegância do method chaining que usamos em LINQ e em middlewares .NET.

- [ ] *(45 min)* Sintaxe pipe (`|`): recompilar lógicas compondo `Prompt | Model | Parser`.
- [ ] *(45 min)* Protocolo Runnable: explorar a interface padronizada para execução assíncrona e paralela.
- [ ] *(45 min)* Praticar cada método (`.invoke()`, `.batch()`, `.stream()`) com o mesmo prompt, comparando latência percebida.
- [ ] *(45 min)* Teste automatizado: `pytest` validando que a chain `Prompt | Model | Parser` retorna o schema/tipo esperado do parser (ex.: `PydanticOutputParser`).

**Tabela comparativa — Interface Runnable:**

| Método | Comportamento | Analogia .NET |
|---|---|---|
| `.invoke()` | Execução síncrona simples | `Execute()` |
| `.batch()` | Processa múltiplas entradas em paralelo | `Parallel.ForEach()` |
| `.stream()` | Retorna a resposta em pedaços (tokens) | `IAsyncEnumerable` |

**Pronto quando:** a mesma chain roda corretamente nos três modos e o teste do parser passa.

---

## Semana 2 — Orquestração Complexa e Estado (9h)

### Dia 1 — Design de Grafos com LangGraph (~3h)

Objetivo: substituir chains lineares por grafos de estado cíclicos, ideais para fluxos de auto-correção.

- [ ] *(40 min)* Estado (`TypedDict`): definir o contrato de estado para governança de microserviços.
- [ ] *(60 min)* Nós e bordas: grafo com nós dedicados para busca em documentação (RAG) e consulta a logs (MCP).
- [ ] *(60 min)* Bordas condicionais: lógica de decisão do LLM ("Preciso ler a documentação ou consultar o banco de dados agora?").
- [ ] *(20 min)* Visualizar o grafo gerado (`get_graph().draw_mermaid()` ou similar) e validar visualmente o fluxo esperado.

**Pronto quando:** o grafo compila, o diagrama gerado corresponde ao fluxo desenhado, e a borda condicional escolhe corretamente entre RAG e MCP em pelo menos 2 cenários de teste manual.

### Dia 2 — Integração Agente + Ferramentas MCP (~3h)

Objetivo: conectar o "cérebro" (LLM) aos "braços" (tools MCP) usando a base em SQL para validação.

- [ ] *(50 min)* Tool Node: integrar o servidor MCP da Semana 1 ao grafo do LangGraph.
- [ ] *(70 min)* Ciclo de auto-correção: se o MCP retornar erro de sintaxe SQL, o LLM analisa o erro, corrige a query usando o schema conhecido e tenta novamente (loop de feedback).
- [ ] *(30 min)* Limitar o loop de auto-correção a um número máximo de tentativas (ex.: 3), evitando loop infinito — análogo a um retry policy com backoff no .NET.
- [ ] *(30 min)* Teste automatizado: simular uma query malformada e validar que o agente converge para uma query válida dentro do limite de tentativas.

**Pronto quando:** o agente corrige uma query SQL malformada sem intervenção manual e respeita o limite de tentativas nos testes.

### Dia 3 — Persistência, Memória e Validação (~3h)

Objetivo: fechar a semana com padrões de resiliência e observabilidade de produção.

- [ ] *(40 min)* Checkpointer: persistência com SQLite no LangGraph para manter o estado da conversa entre reinicializações.
- [ ] *(30 min)* System Prompt: configurar o papel de "Especialista em Arquitetura de Sistemas Distribuídos e Governança".
- [ ] *(60 min)* Teste de integração: simular o agente detectando um erro de "Timeout" via log (MCP) e sugerindo a implementação de um "Circuit Breaker" (RAG).
- [ ] *(50 min)* Validar que, ao reiniciar o processo, o checkpointer restaura o estado da conversa anterior (teste manual: matar e religar o processo).

**Pronto quando:** o teste de integração passa de ponta a ponta e o estado sobrevive a um restart do processo.

---

## Semana 3 — Produção e Operação (6h, opcional/extensão)

Objetivo: cobrir as lacunas entre "funciona no notebook" e "roda em produção" — natural para quem vem de arquitetura .NET e já pensa em SLA, custo e segurança.

### Dia 1 — Observabilidade Real com LangSmith (~2h)

- [ ] Configurar tracing de ponta a ponta no agente da Semana 2.
- [ ] Identificar, em um trace real, onde está o maior custo de tokens e a maior latência do grafo.
- [ ] Comparar o custo estimado por execução do agente com um teto definido por você (ex.: R$/consulta).

### Dia 2 — Segurança de Prompts e Tools (~2h)

- [ ] Prompt injection: testar o agente com uma entrada maliciosa tentando alterar a instrução do system prompt.
- [ ] Restringir o escopo da tool SQL (ex.: permitir apenas `SELECT`, bloquear `DROP`/`DELETE`/`UPDATE`) — analogia a permissões de usuário de banco de dados/least privilege.
- [ ] Validar/sanitizar a saída do LLM antes de qualquer ação automatizada (ex.: nunca executar SQL gerado sem validação de allowlist).

### Dia 3 — Deploy e Custo (~2h)

- [ ] Empacotar o agente como serviço (ex.: FastAPI + `uv`) e definir o `Dockerfile` usando `uv` para instalar dependências de forma determinística.
- [ ] Definir estratégia de rate limiting e fallback para indisponibilidade do provedor de LLM — analogia a Circuit Breaker/Polly no .NET.
- [ ] Registrar uma estimativa de custo mensal com base no volume esperado de execuções.

---

## Tabela de Equivalência: Workflow Legado vs. uv

| Comando legado (pip/venv/python) | Comando uv | Analogia .NET |
|---|---|---|
| `python -m venv .venv` | `uv init` / `uv venv` | `dotnet new` |
| `pip install <package>` | `uv add <package>` | `dotnet add package` |
| `pip install -r requirements.txt` | `uv sync` | `dotnet restore` |
| `python script.py` | `uv run script.py` | `dotnet run` |
| `pip freeze > requirements.txt` | Gerenciado via `uv.lock` | `packages.lock.json` |
| N/A | `pyproject.toml` | `.csproj` |

---

## Recursos e Próximos Passos

- **LangChain Academy**: curso fundamental para dominar orquestração de agentes em nível profissional.
- **LangSmith (Observabilidade)**: essencial para depuração e inspeção de cadeias de raciocínio em produção — praticado na Semana 3.
- **LangChain Documentation**: referência técnica obrigatória para a interface Runnable.
- **LangChain OpenTutorial**: exemplos práticos de RAG e integração de modelos.
