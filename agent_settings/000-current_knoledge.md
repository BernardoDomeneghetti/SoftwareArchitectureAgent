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

### 2026-08-11 — Semana 1, Dia 3 (LCEL — pipe syntax e Runnable protocol)

- Autocorrigiu a hipótese inicial de que `__or__`/`\|` executaria a chain imediatamente na composição — reconheceu, ao ser questionado sobre a ordem temporal dos eventos, que o operador só **registra** os passos, e a execução real fica para `.invoke()`. *Evidência: identificou sozinho a falha no próprio raciocínio ao ser confrontado com a linha de código real.*
- Propôs, sem receber a resposta pronta, um contrato genérico (`IRunnable<TIn, TOut>` com método único parametrizado, análogo a `IRequestHandler<TRequest,TResponse>`) como solução para heterogeneidade de tipos numa chain — chegando muito perto do nome real do conceito (Runnable protocol) antes de ele ser revelado.
- Deduziu corretamente, a partir do contrato genérico, a regra de compatibilidade de tipos entre componentes encadeáveis (`TOut` de um = `TIn` do próximo).
- Mapeou corretamente `.batch()` do LCEL para o padrão de disparar múltiplas `Task`s e aguardá-las juntas (`Task.WhenAll`), com a lógica certa mesmo errando o nome exato do método.
