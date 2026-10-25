# sdd-task-analyzer

[![CI](https://github.com/arthuramaral-stack/sdd-task-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/arthuramaral-stack/sdd-task-analyzer/actions/workflows/ci.yml)

Módulo **TaskAnalyzer**: calcula métricas de produtividade (tempo médio de conclusão, taxa de atraso e indicadores por prioridade) a partir de uma lista de tarefas.

Projeto do **Bootcamp III**, desenvolvido com **Spec-Driven Development (SDD)**. O código em `src/` foi gerado por assistente de IA a partir da especificação e das regras de contexto, validado pelo Test Harness e homologado por revisão humana. Na Fase 3, o projeto ganhou integração contínua no GitHub Actions e execução isolada em Docker.

| Fase | Papel | Entregas |
|---|---|---|
| 1 | Arquiteto de Especificações | SDD e `CONTEXT_RULES.md` |
| 2 | Piloto de IA e QA | Código via IA, Test Harness com pytest e versionamento |
| 3 | DevOps e Governança | CI/CD, Docker e auditoria ética da IA |

## Estrutura

```
sdd-task-analyzer/
├── .github/
│   └── workflows/
│       └── ci.yml                   # Pipeline de CI (GitHub Actions)
├── Dockerfile                       # Imagem python:3.11-slim que roda os testes
├── docker-compose.yml               # Serviço "tests": docker compose run --rm tests
├── .dockerignore
├── CONTEXT_RULES.md                 # Regras de governança para a IA (v1.1)
├── specs/
│   ├── system_design_document.pdf   # SDD formal (versão PDF da spec)
│   ├── task_analyzer_spec.md        # Contrato SDD e cenários de aceite CA01–CA07
│   └── requirements.yaml            # Requisitos rastreáveis: RN → cenário → teste
├── tests/
│   └── test_harness.py              # Test Harness (pytest)
├── src/
│   └── task_analyzer.py             # Implementação gerada via IA e homologada
├── pytest.ini                       # Coloca a raiz no sys.path para o pytest
├── requirements.txt                 # Dependência autorizada (pytest, versão fixa)
└── README.md
```

## Como executar

### Com Docker (recomendado)

Não precisa instalar Python, só o Docker.

```bash
docker compose run --rm tests
```

Ou, passo a passo:

```bash
docker build -t sdd-task-analyzer .
docker run --rm sdd-task-analyzer
```

### Local

Requisitos: **Python 3.11+**.

```bash
python -m venv venv
# Windows: venv\Scripts\activate | Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
pytest tests/test_harness.py -v
```

Resultado esperado: **19 passed**.

## Integração contínua

O workflow [`ci.yml`](.github/workflows/ci.yml) roda em todo **push** ou **Pull Request** nas branches `main` e `develop`:

1. **Test Harness:** `ubuntu-latest` com Python 3.11, instala o `requirements.txt` e executa `pytest tests/test_harness.py -v`.
2. **Docker:** se os testes passarem, faz o build da imagem e roda a suíte dentro do container.

A `main` só recebe código por Pull Request com o CI verde (CONTEXT_RULES 3.5).

## Uso

```python
from datetime import datetime, timezone
from src.task_analyzer import Tarefa, analisar_tarefas

utc = lambda h, m=0: datetime(2026, 9, 1, h, m, tzinfo=timezone.utc)

relatorio = analisar_tarefas([
    Tarefa(1, "Configurar ambiente", "alta", "concluida",
           utc(7), utc(10), utc(8), utc(9)),
])
print(relatorio["tempo_medio_conclusao_min"])  # 60.0
```

## Cenários cobertos pelo Test Harness

| Cenário | O que valida |
|---|---|
| CA01 | Métricas corretas com a massa padrão (totais, tempo médio geral e por prioridade, taxa de atraso) |
| CA02 | `data_conclusao` anterior a `data_inicio` → `DataInvalidaError` |
| CA03 | Nenhuma tarefa concluída → `SemTarefasConcluidasError` (nunca `ZeroDivisionError`) |
| CA04 | Arredondamento, prazo exato não é atraso, prioridade vazia retorna `None` |
| CA05 | Entradas inválidas (lista vazia, enum inválido, id duplicado/zero, título vazio) → `EntradaInvalidaError` |
| CA06 | Datas sem fuso ou incoerentes → `DataInvalidaError` |
| CA07 | A lista de entrada não é modificada (função pura) |

O mapa completo de regra de negócio → cenário → teste está em [`specs/requirements.yaml`](specs/requirements.yaml).

## Fluxo de trabalho

- `main`: sempre estável, só recebe Pull Request com CI verde.
- `develop`: integração das features antes da `main`.
- `feature/*`: uma branch por funcionalidade, integrada via Pull Request com checklist de homologação.
- Commits no padrão Conventional Commits (`feat:`, `test:`, `docs:`, `ci:`, `build:`, `chore:`).

## Autor

Arthur Amaral dos Santos — Análise e Desenvolvimento de Sistemas (CEUB)
