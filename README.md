# sdd-task-analyzer

Módulo **TaskAnalyzer**: calcula métricas de produtividade (tempo médio de conclusão, taxa de atraso e indicadores por prioridade) a partir de uma lista de tarefas.

Projeto do **Bootcamp III**, desenvolvido com **Spec-Driven Development (SDD)**. O código em `src/` foi gerado por assistente de IA a partir da especificação e das regras de contexto, validado pelo Test Harness e homologado por revisão humana.

**Status do build:** ✅ 19 testes passando (`python -m pytest -v tests/`)

## Estrutura

```
sdd-task-analyzer/
├── README.md                  # Este arquivo
├── CONTEXT_RULES.md           # Regras de governança para a IA
├── requirements.txt           # Dependências autorizadas (pytest)
├── .gitignore
├── specs/
│   └── task_analyzer_spec.md  # Contrato SDD e cenários de aceite CA01–CA07
├── tests/
│   └── test_harness.py        # Test Harness (pytest)
└── src/
    └── task_analyzer.py       # Implementação gerada via IA e homologada
```

## Como executar

Requisitos: **Python 3.11+**.

```bash
python -m venv venv
# Windows: venv\Scripts\activate | Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python -m pytest -v tests/
```

> Rode sempre a partir da raiz do repositório, com `python -m pytest`, para que o pacote `src` seja encontrado.

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

## Fluxo de trabalho

- `main`: sempre estável, com testes passando.
- `feature/*`: uma branch por funcionalidade, integrada à `main` via Pull Request com checklist de homologação.
- Commits no padrão Conventional Commits (`feat:`, `test:`, `docs:`, `chore:`).

## Autor

Arthur Amaral dos Santos — Análise e Desenvolvimento de Sistemas (CEUB)
