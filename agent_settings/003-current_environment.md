# Ambiente Atual — Plano de Estudos de Engenharia de IA

Contexto acumulado até agora (Dia 01, Semana 01) para uso como referência em conversas futuras.

## Objetivo do plano

Desenvolver um agente especializado em Arquitetura de Sistemas Distribuídos e Governança, capaz de:

- Analisar logs de microserviços para detectar falhas (via protocolo MCP).
- Consultar documentação técnica para buscar padrões de resiliência (via RAG).
- Sugerir implementações como Circuit Breaker ou Retry Pattern ao identificar erros de timeout ou latência.

A tarefa do Dia 1 é construir um sistema RAG (Retrieval-Augmented Generation) "do zero", sem usar abstrações prontas do LangChain, para entender a matemática por trás de embeddings e busca vetorial.

## Decisão de override em relação às fontes originais

As fontes do plano original prescrevem `venv` + `pip`. O usuário optou por substituir esse fluxo por **uv** (gerenciador de pacotes Python escrito em Rust, focado em performance). O mentor não altera os documentos-fonte fisicamente; a tradução `venv/pip → uv` é feita em tempo real durante a execução. Foi gerado um plano de estudos paralelo, idêntico ao original, mas adaptado para uv.

Tabela de equivalência usada (.NET ↔ Python/uv):

| .NET | Python / uv |
|---|---|
| `.csproj` | `pyproject.toml` |
| `packages.lock.json` | `uv.lock` |
| `dotnet new` / `dotnet new console` | `uv init` |
| `dotnet add package` | `uv add` |
| `dotnet restore` | equivalente a instalar via `uv add` / sync |
| `appsettings.json` / User Secrets | arquivo `.env` (via `python-dotenv`) |
| `Environment.GetEnvironmentVariable("NOME")` | `os.getenv("NOME")` |
| `ConfigurationBuilder().AddEnvironmentVariables()` | `load_dotenv()` |

## Estado do projeto (o que já foi executado)

1. Ambiente/projeto inicializado com `uv init`, que gerou o arquivo **`pyproject.toml`** (equivalente ao `.csproj`).
2. Dependências instaladas com um único comando:
   ```
   uv add openai numpy python-dotenv
   ```
   Isso atualizou o `pyproject.toml` (seção `dependencies`, equivalente ao `<ItemGroup>`/`<PackageReference>`) e gerou o `uv.lock` (equivalente ao `packages.lock.json`).
3. Escopo das dependências: instaladas apenas para este projeto (isoladas), não globalmente — análogo a `dotnet add package` rodado em um `.csproj` específico não afetar outros projetos.

### Core setup inicial (decidido pelo usuário)

As três bibliotecas abaixo foram definidas como núcleo do setup do Dia 1, sem adiar nenhuma:

- **numpy** — cálculos matemáticos e similaridade de cosseno (busca vetorial).
- **openai** — cliente para gerar embeddings (transformar texto em vetores).
- **python-dotenv** — carregar variáveis de ambiente/segredos a partir de arquivo local (`.env`), evitando hardcoding de API keys.

## Gerenciamento de credenciais (API Key da OpenAI)

- O usuário já tinha a `OPENAI_API_KEY` armazenada nas variáveis de ambiente do SO.
- Decidiu, ainda assim, também armazená-la em um arquivo **`.env`** local, para garantir que o projeto seja "clonar e rodar" para outros desenvolvedores sem depender de configuração global do SO (equivalente ao `appsettings.Development.json`).
- Nome padrão de variável esperado pelas bibliotecas de IA: `OPENAI_API_KEY`.

### Código Python já validado (main.py, em construção)

```python
from dotenv import load_dotenv

load_dotenv()
```

- `from dotenv import load_dotenv`: importa especificamente a função `load_dotenv` do módulo `dotenv` (sintaxe "de [origem] importe [membro]").
- `load_dotenv()`: lê o arquivo `.env` e injeta os valores como variáveis de ambiente no processo, tornando-os acessíveis via `os.getenv("OPENAI_API_KEY")`.

## Pendências / próximo passo em aberto

- **Pergunta em aberto no momento:** onde o arquivo `.env` deve ficar no projeto (ainda não respondida na conversa).
- Próximos tópicos previstos no plano do Dia 1: geração de embeddings com OpenAI, implementação manual de similaridade de cosseno com numpy, e montagem do pipeline de recuperação (retrieval) do RAG.

## Notas de estilo/preferência do usuário

- Usuário tem forte background em .NET/C#, Docker e sistemas distribuídos — analogias com esse ecossistema são o formato didático usado ao longo do plano.
- Prefere entender o processo "sob o capô" antes de usar comandos que aglutinam múltiplas etapas (ex.: preferiu ver `uv venv` separadamente antes de um comando único).