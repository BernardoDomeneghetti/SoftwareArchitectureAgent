# Déficits de Conhecimento

> **Memória viva.** Diferente dos arquivos `000-*`, este não rastreia o progresso no plano de estudos de IA — rastreia lacunas de conhecimento do aluno reveladas como efeito colateral das perguntas socráticas. Principalmente C#/.NET (base usada nas analogias), mas também fundamentos gerais de engenharia (ex.: logging) quando surgirem na conversa.
>
> **Protocolo:** toda vez que uma pergunta feita ao aluno envolver um conceito técnico — .NET/C# ou fundamentos gerais de engenharia — e ele **não souber responder** (ou souber só parcialmente), registre aqui: data, conceito, o contexto que motivou a pergunta, e o que ele respondeu. Isso vira uma lista de estudo para ele revisitar depois, por conta própria — fora do escopo deste mentor. Não é preciso perguntar ao aluno antes de registrar; é registro silencioso, como os arquivos `000-*`.
>
> Conceitos que ele demonstrou dominar durante as perguntas (não são déficit) não entram aqui — ficam em `000-current_knoledge.md`.

---

## 1. Baseline declarado na contextualização inicial

O que o aluno **afirmou** dominar ao descrever seu perfil (ver `000-current_knoledge.md`, seção 1) — ainda não testado em detalhe pelas perguntas socráticas, listado aqui como ponto de partida, não como déficit:

- Sistemas distribuídos, microserviços.
- Kubernetes, Docker.
- Redes e APIs.
- Bancos de dados relacionais (domínio) e NoSQL (intermediário).
- Base em arquitetura de software.

---

## 2. Déficits identificados durante as sessões

| Data | Conceito | Contexto da pergunta (o que motivou) | O que o aluno respondeu |
|---|---|---|---|
| 2026-08-11 | Comunicação entre processos (IPC) na mesma máquina — ex.: redirecionar stdin/stdout de um processo filho iniciado via `Process` (.NET) | Entender o transporte *stdio* do MCP (client inicia o server localmente) | "não sei responder isso nem em .NET" |
| 2026-08-11 | Redirecionamento de streams padrão (stdout/stdin/stderr) e pipe (`\|`) no terminal | Mesma linha de raciocínio acima, tentando chegar a IPC via um caminho mais básico | Não conhecia o uso de `>` para redirecionar saída de programa para arquivo |
| 2026-08-11 | `[Flags]` em enums e uso de `\|` bitwise sobre eles (.NET) | Ponte para entender o operador `\|` do Python antes de chegar ao uso do LangChain (LCEL) | "Não conheço o conceito de flags em Enums" |
| 2026-08-11 | Sobrecarga de operadores em C# (`public static Foo operator +(Foo a, Foo b)`) | Explicar por que LangChain consegue reaproveitar `\|` para compor `Prompt \| Model \| Parser` (via `__or__` do Python) | "nossa nunca imaginei que isso fosse possível" — não conhecia a existência do recurso |
| 2026-08-11 | Nome formal do padrão **Middleware Pipeline** (ASP.NET Core) | Buscar analogia .NET para o comportamento de LCEL (registrar passos, executar só quando o dado real chega) | Reconheceu a prática ("amontagem do pipeline de execução e configuração das injeções de dependência") mas não sabia o nome do conceito |
| 2026-08-11 | `IAsyncEnumerable<T>` + `await foreach` (async streams, C# 8+) | Mapear `.stream()` do LCEL (resposta token a token) para o equivalente .NET | "não sei" — inicialmente pareceu conhecer `yield return`, mas depois admitiu que também não domina o `yield` em si |
| 2026-08-11 | `yield return` — iteradores/geradores em C# (pausar e retomar execução de um método) | Mesma linha de raciocínio, ao aprofundar em `.stream()` | "eu também não sei como funciona o yield no C#" |
| 2026-08-11 | Logging estruturado — níveis de severidade (info/warning/error), separação entre dado estruturado e mensagem livre | Desenhando o schema da tabela de logs de microserviços para a tool MCP; avaliando se `message` livre basta ou se precisa de coluna de status/nível | "eu não sei como funciona logging direito" — gap geral, não específico de .NET |
| 2026-08-13 | Camada de provider ADO.NET específica por SGBD (`Npgsql` para Postgres) — nunca usou, só passou por ORMs (EF Core/Dapper) que a escondem | Entendendo o papel do `asyncpg` em Python por analogia com a stack de acesso a dados do .NET | Não conhecia o nome `Npgsql` nem tinha clareza de que EF Core/Dapper delegam a comunicação de rede pra essa camada; inicialmente também confundiu "genérico vs. específico" com a camada errada (achou que o `asyncpg` era o "específico" e o provider .NET seria o "genérico"), mas corrigiu sozinho ao ser questionado |
| 2026-08-13 | Minimal APIs do ASP.NET Core — injeção de dependência direto no parâmetro de um método (sem controller/construtor), ex. `[FromServices]` | Buscando o equivalente .NET de como o SDK do MCP injeta o `Context` (com acesso ao pool via `lifespan`) direto no parâmetro de uma função de tool, sem construtor de classe | "não tenho conhecimento de minimal apis" |
| 2026-08-18 | `yield` / generators — tanto em C# (`yield return`) quanto em Python | Introduzindo `@asynccontextmanager` para implementar o `lifespan` do servidor MCP (setup do `asyncpg.Pool` antes do `yield`, teardown depois) | "totalmente novo" — confirma o gap já suspeitado em 2026-08-11 durante LCEL (`.stream()`), agora também em Python, não só em C# |

---

## 3. Como usar esta lista

Cada linha acima é um tópico de estudo autônomo — fora do escopo deste mentor de IA, mas relevante pra reforçar a base técnica que sustenta as analogias usadas aqui. Sugestão: revisar em lote, não um por vez, já que muitos se conectam (streams/IPC; operator overloading/`[Flags]`/dunder methods; middleware pipeline).
