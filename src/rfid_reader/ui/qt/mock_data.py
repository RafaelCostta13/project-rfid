"""Dados exclusivamente fictícios para a aprovação visual da Fase 1 do RF018."""

from dataclasses import dataclass
from enum import StrEnum

from rfid_reader.domain import TagLookupResult, TagLookupStatus


class PrototypeScenario(StrEnum):
    READY = "ready"
    READING = "reading"
    FAILURE = "failure"
    CHECKING = "checking"
    EMPTY = "empty"


class PrototypeTheme(StrEnum):
    CORPORATE = "corporate"
    NAVY = "navy"


@dataclass(frozen=True, slots=True)
class PreviewConnection:
    label: str
    state: str
    description: str


@dataclass(frozen=True, slots=True)
class PreviewSnapshot:
    scenario: PrototypeScenario
    state: str
    title: str
    description: str
    connections: tuple[PreviewConnection, ...]


MOCK_RECORDS = tuple(
    TagLookupResult(
        epc=f"E280691500005029EEA6A27{index}",
        status=TagLookupStatus.FOUND,
        message="Registro fictício; nenhuma consulta ou passagem foi executada.",
        customer=customer,
        invoice_number=f"0001234{index}",
        volume=f"00{index}",
        order_number=f"00005678{index}",
        dock="D01",
        record_status="lido",
    )
    for index, customer in enumerate(
        (
            "Cliente exemplo A",
            "Cliente exemplo B",
            "Cliente exemplo C",
            "Cliente exemplo D",
            "Cliente exemplo E",
        ),
        start=1,
    )
)


def preview_snapshot(scenario: PrototypeScenario) -> PreviewSnapshot:
    """Constrói uma apresentação simulada, sem autoridade sobre equipamentos."""

    state, title, description = {
        PrototypeScenario.READY: ("ok", "Aguardando", "Sistema apto · cenário simulado"),
        PrototypeScenario.READING: ("warning", "Lendo", "Leitura em andamento · cenário simulado"),
        PrototypeScenario.FAILURE: ("error", "Indisponível", "Falha do Sistema · cenário simulado"),
        PrototypeScenario.CHECKING: ("checking", "Verificando", "Verificando conexões · simulação"),
        PrototypeScenario.EMPTY: ("ok", "Aguardando", "Sessão sem registros · cenário simulado"),
    }[scenario]
    connections = tuple(
        PreviewConnection(
            label,
            "checking"
            if scenario is PrototypeScenario.CHECKING
            else "error"
            if label == "Sistema" and scenario is PrototypeScenario.FAILURE
            else "ok",
            "Verificando"
            if scenario is PrototypeScenario.CHECKING
            else "Indisponível"
            if label == "Sistema" and scenario is PrototypeScenario.FAILURE
            else "Disponível"
            if label == "Sistema"
            else "Conectado",
        )
        for label in ("RFID", "Internet", "Comandos", "Sistema")
    )
    return PreviewSnapshot(scenario, state, title, description, connections)
