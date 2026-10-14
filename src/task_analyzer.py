"""Módulo TaskAnalyzer: métricas de produtividade a partir de uma lista de tarefas.

Implementa o contrato definido em specs/task_analyzer_spec.md (versão 1.0),
seguindo as diretrizes de CONTEXT_RULES.md. Usa apenas a biblioteca padrão.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypedDict

logger = logging.getLogger(__name__)

PRIORIDADES_VALIDAS: tuple[str, ...] = ("baixa", "media", "alta")
STATUS_VALIDOS: tuple[str, ...] = ("concluida", "pendente", "cancelada")
STATUS_CONCLUIDA: str = "concluida"
CASAS_DECIMAIS: int = 2
SEGUNDOS_POR_MINUTO: int = 60
PERCENTUAL_TOTAL: int = 100


# --------------------------------------------------------------------------- #
# Exceções do contrato (seção 1.3.4)
# --------------------------------------------------------------------------- #
class TaskAnalyzerError(Exception):
    """Base de todas as exceções do módulo TaskAnalyzer."""


class EntradaInvalidaError(TaskAnalyzerError):
    """Lista ou campos de tarefa com tipo ou valor fora do permitido."""


class DataInvalidaError(TaskAnalyzerError):
    """Datas sem fuso horário ou temporalmente incoerentes."""


class SemTarefasConcluidasError(TaskAnalyzerError):
    """Nenhuma tarefa concluída na lista (evita divisão por zero)."""


# --------------------------------------------------------------------------- #
# Tipos públicos (seção 1.3.1)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Tarefa:
    """Tarefa recebida pelo analisador.

    Attributes:
        id_tarefa: Identificador único e positivo da tarefa.
        titulo: Título não vazio.
        prioridade: Um de "baixa", "media" ou "alta".
        status: Um de "concluida", "pendente" ou "cancelada".
        data_criacao: Data/hora de criação (UTC, com fuso).
        prazo: Data/hora limite (UTC, com fuso).
        data_inicio: Início da execução; obrigatório se concluída.
        data_conclusao: Fim da execução; obrigatório só se concluída.
    """

    id_tarefa: int
    titulo: str
    prioridade: str
    status: str
    data_criacao: datetime
    prazo: datetime
    data_inicio: datetime | None = None
    data_conclusao: datetime | None = None


class IndicadorPrioridade(TypedDict):
    """Indicadores calculados para uma prioridade."""

    quantidade_concluidas: int
    tempo_medio_conclusao_min: float | None
    taxa_atraso_percentual: float | None


class RelatorioMetricas(TypedDict):
    """Relatório final retornado por analisar_tarefas."""

    total_tarefas: int
    total_concluidas: int
    tempo_medio_conclusao_min: float
    taxa_atraso_percentual: float
    indicadores_por_prioridade: dict[str, IndicadorPrioridade]


# --------------------------------------------------------------------------- #
# Validação (RN05, RN06, RN07, RN10)
# --------------------------------------------------------------------------- #
def _validar_lista(tarefas: object) -> None:
    """Garante que a entrada é uma lista não vazia de Tarefa.

    Args:
        tarefas: Objeto recebido pela função pública.

    Raises:
        EntradaInvalidaError: Se não for list, estiver vazia ou tiver itens
            que não são Tarefa.
    """
    if not isinstance(tarefas, list):
        raise EntradaInvalidaError("A entrada tarefas deve ser uma lista.")
    if not tarefas:
        raise EntradaInvalidaError("A lista de tarefas não pode estar vazia.")
    for posicao, item in enumerate(tarefas):
        if not isinstance(item, Tarefa):
            raise EntradaInvalidaError(
                f"Item na posição {posicao} não é uma Tarefa."
            )


def _validar_campos(tarefa: Tarefa, ids_vistos: set[int]) -> None:
    """Valida id, título, prioridade e status de uma tarefa.

    Args:
        tarefa: Tarefa a validar.
        ids_vistos: Ids já encontrados na lista (atualizado aqui).

    Raises:
        EntradaInvalidaError: Se algum campo violar o contrato.
    """
    id_tarefa = tarefa.id_tarefa
    if isinstance(id_tarefa, bool) or not isinstance(id_tarefa, int):
        raise EntradaInvalidaError(f"Tarefa {id_tarefa}: id_tarefa deve ser int.")
    if id_tarefa <= 0:
        raise EntradaInvalidaError(f"Tarefa {id_tarefa}: id_tarefa deve ser > 0.")
    if id_tarefa in ids_vistos:
        raise EntradaInvalidaError(f"Tarefa {id_tarefa}: id_tarefa duplicado.")
    ids_vistos.add(id_tarefa)
    if not isinstance(tarefa.titulo, str) or not tarefa.titulo.strip():
        raise EntradaInvalidaError(f"Tarefa {id_tarefa}: titulo vazio.")
    if tarefa.prioridade not in PRIORIDADES_VALIDAS:
        raise EntradaInvalidaError(
            f"Tarefa {id_tarefa}: prioridade inválida '{tarefa.prioridade}'."
        )
    if tarefa.status not in STATUS_VALIDOS:
        raise EntradaInvalidaError(
            f"Tarefa {id_tarefa}: status inválido '{tarefa.status}'."
        )


def _validar_fuso(tarefa: Tarefa) -> None:
    """Exige datas timezone-aware em UTC (RN05).

    Args:
        tarefa: Tarefa a validar.

    Raises:
        DataInvalidaError: Se alguma data informada não tiver fuso UTC.
    """
    campos: dict[str, datetime | None] = {
        "data_criacao": tarefa.data_criacao,
        "prazo": tarefa.prazo,
        "data_inicio": tarefa.data_inicio,
        "data_conclusao": tarefa.data_conclusao,
    }
    for nome_campo, valor in campos.items():
        if valor is None:
            continue
        if not isinstance(valor, datetime):
            raise DataInvalidaError(
                f"Tarefa {tarefa.id_tarefa}: {nome_campo} deve ser datetime."
            )
        if valor.tzinfo is None or valor.utcoffset() != timedelta(0):
            raise DataInvalidaError(
                f"Tarefa {tarefa.id_tarefa}: {nome_campo} sem fuso horário UTC."
            )


def _validar_coerencia_datas(tarefa: Tarefa) -> None:
    """Valida obrigatoriedade e ordem temporal das datas (RN07).

    Args:
        tarefa: Tarefa com campos e fusos já validados.

    Raises:
        DataInvalidaError: Se as datas forem incoerentes com o status.
    """
    id_tarefa = tarefa.id_tarefa
    if tarefa.data_criacao is None or tarefa.prazo is None:
        raise DataInvalidaError(
            f"Tarefa {id_tarefa}: data_criacao e prazo são obrigatórios."
        )
    if tarefa.prazo < tarefa.data_criacao:
        raise DataInvalidaError(f"Tarefa {id_tarefa}: prazo anterior a data_criacao.")
    if tarefa.data_inicio is not None and tarefa.data_inicio < tarefa.data_criacao:
        raise DataInvalidaError(
            f"Tarefa {id_tarefa}: data_inicio anterior a data_criacao."
        )
    if tarefa.status != STATUS_CONCLUIDA:
        if tarefa.data_conclusao is not None:
            raise DataInvalidaError(
                f"Tarefa {id_tarefa}: data_conclusao preenchida em tarefa não "
                "concluída."
            )
        return
    if tarefa.data_inicio is None:
        raise DataInvalidaError(f"Tarefa {id_tarefa}: data_inicio ausente.")
    if tarefa.data_conclusao is None:
        raise DataInvalidaError(f"Tarefa {id_tarefa}: data_conclusao ausente.")
    if tarefa.data_conclusao < tarefa.data_inicio:
        raise DataInvalidaError(
            f"Tarefa {id_tarefa}: data_conclusao anterior a data_inicio."
        )


def _validar_tarefas(tarefas: object) -> None:
    """Valida toda a entrada em modo fail-fast (RN06).

    Args:
        tarefas: Objeto recebido pela função pública.

    Raises:
        EntradaInvalidaError: Lista ou campos inválidos.
        DataInvalidaError: Datas sem fuso ou incoerentes.
    """
    _validar_lista(tarefas)
    ids_vistos: set[int] = set()
    for tarefa in tarefas:  # type: ignore[union-attr]
        _validar_campos(tarefa, ids_vistos)
        _validar_fuso(tarefa)
        _validar_coerencia_datas(tarefa)
