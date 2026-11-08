"""Resultados fictícios para testar somente a apresentação da aplicação."""

from __future__ import annotations

from rfid_reader.domain import TagLookupResult, TagLookupStatus


def simulated_result(sequence: int, *, extra_box: bool) -> TagLookupResult:
    """Cria um EPC hexadecimal único e dados explicitamente fictícios."""

    return TagLookupResult(
        epc=f"424D57000000000000{sequence:06X}",
        status=TagLookupStatus.EXTRA_BOX if extra_box else TagLookupStatus.FOUND,
        message="Registro simulado; nenhuma operação externa foi executada.",
        supplier="BMW do Brasil Ltda",
        customer="DEALER TESTE",
        invoice_number="1198497",
        volume="1/1",
        order_number="0007818432",
        dock="DOCA 42",
        record_status="pendente",
    )
