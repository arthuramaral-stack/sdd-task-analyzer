"""Test Harness do TaskAnalyzer: cenários de aceite CA01–CA07.

Tradução fiel da seção 2 de specs/task_analyzer_spec.md. Os valores esperados
não podem ser alterados (CONTEXT_RULES 3.2, item 2).

Execução: python -m pytest -v tests/
"""

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from src.task_analyzer import (
    DataInvalidaError,
    EntradaInvalidaError,
    SemTarefasConcluidasError,
    TaskAnalyzerError,
    Tarefa,
    analisar_tarefas,
)


def utc(hora: int, minuto: int = 0) -> datetime:
    """Cria um datetime em 01/09/2026 no fuso UTC."""
    return datetime(2026, 9, 1, hora, minuto, tzinfo=timezone.utc)


def tarefa_concluida(
    id_tarefa: int,
    inicio: datetime,
    conclusao: datetime,
    prazo: datetime,
    prioridade: str = "alta",
) -> Tarefa:
    """Atalho para montar uma tarefa concluída criada às 07:00 UTC."""
    return Tarefa(
        id_tarefa=id_tarefa,
        titulo=f"Tarefa {id_tarefa}",
        prioridade=prioridade,
        status="concluida",
        data_criacao=utc(7),
        prazo=prazo,
        data_inicio=inicio,
        data_conclusao=conclusao,
    )


@pytest.fixture
def massa_padrao() -> list[Tarefa]:
    """Massa de dados padrão MD01 (seção 2.1)."""
    criacao = utc(7)
    return [
        Tarefa(1, "Configurar ambiente", "alta", "concluida",
               criacao, utc(10), utc(8), utc(9)),
        Tarefa(2, "Corrigir bug de login", "alta", "concluida",
               criacao, utc(9), utc(8), utc(10)),
        Tarefa(3, "Revisar PR", "media", "concluida",
               criacao, utc(12), utc(9), utc(9, 30)),
        Tarefa(4, "Atualizar documentação", "baixa", "concluida",
               criacao, utc(12), utc(10), utc(13)),
        Tarefa(5, "Criar dashboard", "media", "pendente",
               criacao, utc(18), utc(11), None),
        Tarefa(6, "Migrar servidor", "baixa", "cancelada",
               criacao, utc(18), None, None),
    ]


# --------------------------------------------------------------------------- #
# CA01 — Sucesso: métricas corretas
# --------------------------------------------------------------------------- #
def test_ca01_metricas_corretas_com_massa_padrao(massa_padrao: list[Tarefa]) -> None:
    resultado = analisar_tarefas(massa_padrao)

    assert resultado == {
        "total_tarefas": 6,
        "total_concluidas": 4,
        "tempo_medio_conclusao_min": 97.5,
        "taxa_atraso_percentual": 50.0,
        "indicadores_por_prioridade": {
            "baixa": {
                "quantidade_concluidas": 1,
                "tempo_medio_conclusao_min": 180.0,
                "taxa_atraso_percentual": 100.0,
            },
            "media": {
                "quantidade_concluidas": 1,
                "tempo_medio_conclusao_min": 30.0,
                "taxa_atraso_percentual": 0.0,
            },
            "alta": {
                "quantidade_concluidas": 2,
                "tempo_medio_conclusao_min": 90.0,
                "taxa_atraso_percentual": 50.0,
            },
        },
    }


# --------------------------------------------------------------------------- #
# CA02 — Exceção: conclusão antes do início
# --------------------------------------------------------------------------- #
def test_ca02_conclusao_antes_do_inicio_lanca_data_invalida() -> None:
    tarefa_7 = tarefa_concluida(7, inicio=utc(10), conclusao=utc(9), prazo=utc(12))

    with pytest.raises(DataInvalidaError, match=r"Tarefa 7.*data_conclusao"):
        analisar_tarefas([tarefa_7])


# --------------------------------------------------------------------------- #
# CA03 — Exceção: sem tarefas concluídas (proteção contra divisão por zero)
# --------------------------------------------------------------------------- #
def test_ca03_sem_tarefas_concluidas_lanca_excecao_especifica(
    massa_padrao: list[Tarefa],
) -> None:
    somente_pendente_e_cancelada = massa_padrao[4:]

    with pytest.raises(SemTarefasConcluidasError, match="concluida"):
        analisar_tarefas(somente_pendente_e_cancelada)


def test_ca03_nunca_lanca_zero_division_error(massa_padrao: list[Tarefa]) -> None:
    try:
        analisar_tarefas(massa_padrao[4:])
    except ZeroDivisionError:  # pragma: no cover - falha explícita do contrato
        pytest.fail("ZeroDivisionError não pode escapar do analisador.")
    except SemTarefasConcluidasError:
        pass


# --------------------------------------------------------------------------- #
# CA04 — Borda: arredondamento, prazo exato e prioridade vazia
# --------------------------------------------------------------------------- #
def test_ca04_arredondamento_prazo_exato_e_prioridade_vazia() -> None:
    tarefas = [
        tarefa_concluida(1, inicio=utc(8), conclusao=utc(8, 10), prazo=utc(8, 10)),
        tarefa_concluida(2, inicio=utc(8), conclusao=utc(8, 10), prazo=utc(9)),
        tarefa_concluida(3, inicio=utc(8), conclusao=utc(8, 11), prazo=utc(8, 10)),
    ]

    resultado = analisar_tarefas(tarefas)

    assert resultado["tempo_medio_conclusao_min"] == 10.33
    assert resultado["taxa_atraso_percentual"] == 33.33
    vazio = {
        "quantidade_concluidas": 0,
        "tempo_medio_conclusao_min": None,
        "taxa_atraso_percentual": None,
    }
    assert resultado["indicadores_por_prioridade"]["baixa"] == vazio
    assert resultado["indicadores_por_prioridade"]["media"] == vazio
    assert resultado["indicadores_por_prioridade"]["alta"] == {
        "quantidade_concluidas": 3,
        "tempo_medio_conclusao_min": 10.33,
        "taxa_atraso_percentual": 33.33,
    }


# --------------------------------------------------------------------------- #
# CA05 — Exceção: entradas inválidas (parametrizado)
# --------------------------------------------------------------------------- #
def _tarefa_base() -> Tarefa:
    return tarefa_concluida(1, inicio=utc(8), conclusao=utc(9), prazo=utc(10))


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param([], id="a_lista_vazia"),
        pytest.param([replace(_tarefa_base(), prioridade="urgente")],
                     id="b_prioridade_urgente"),
        pytest.param([replace(_tarefa_base(), status="feito")],
                     id="c_status_feito"),
        pytest.param([_tarefa_base(), replace(_tarefa_base(), titulo="Outra")],
                     id="d_id_duplicado"),
        pytest.param([replace(_tarefa_base(), id_tarefa=0)], id="e_id_zero"),
        pytest.param([replace(_tarefa_base(), titulo=" ")], id="f_titulo_vazio"),
    ],
)
def test_ca05_entradas_invalidas_lancam_entrada_invalida(
    entrada: list[Tarefa],
) -> None:
    with pytest.raises(EntradaInvalidaError):
        analisar_tarefas(entrada)


# --------------------------------------------------------------------------- #
# CA06 — Exceção: datas sem fuso ou incoerentes (parametrizado)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "tarefa",
    [
        pytest.param(replace(_tarefa_base(), data_criacao=datetime(2026, 9, 1, 7)),
                     id="a_data_criacao_sem_fuso"),
        pytest.param(replace(_tarefa_base(), prazo=utc(6)),
                     id="b_prazo_antes_da_criacao"),
        pytest.param(replace(_tarefa_base(), data_conclusao=None),
                     id="c_concluida_sem_data_conclusao"),
        pytest.param(replace(_tarefa_base(), status="pendente"),
                     id="d_pendente_com_data_conclusao"),
    ],
)
def test_ca06_datas_incoerentes_lancam_data_invalida(tarefa: Tarefa) -> None:
    with pytest.raises(DataInvalidaError):
        analisar_tarefas([tarefa])


# --------------------------------------------------------------------------- #
# CA07 — Função pura: entrada não é alterada
# --------------------------------------------------------------------------- #
def test_ca07_lista_de_entrada_nao_e_modificada(massa_padrao: list[Tarefa]) -> None:
    # Tarefa é frozen, então uma cópia rasa basta para detectar mudanças na lista.
    copia = list(massa_padrao)

    analisar_tarefas(massa_padrao)

    assert massa_padrao == copia
    assert all(atual is original for atual, original in zip(massa_padrao, copia))


# --------------------------------------------------------------------------- #
# Contrato de exceções: todas herdam da base comum (seção 1.3.4)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "excecao",
    [EntradaInvalidaError, DataInvalidaError, SemTarefasConcluidasError],
)
def test_excecoes_herdam_de_task_analyzer_error(excecao: type[Exception]) -> None:
    assert issubclass(excecao, TaskAnalyzerError)
