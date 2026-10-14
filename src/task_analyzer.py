"""Módulo TaskAnalyzer: métricas de produtividade a partir de uma lista de tarefas.

Implementa o contrato definido em specs/task_analyzer_spec.md (versão 1.0),
seguindo as diretrizes de CONTEXT_RULES.md. Usa apenas a biblioteca padrão.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
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
