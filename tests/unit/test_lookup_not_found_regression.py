import json

from rfid_reader.domain import TagLookupSessionSummary, TagLookupStatus
from rfid_reader.integrations.sharepoint_client import HttpResponse, SharePointLookupClient


def test_false_api_result_is_not_accepted_by_found_collection() -> None:
    payload = {
        "body": {
            "sucesso": False,
            "mensagem": "EPC não localizado",
            "epc": "AAA1",
        }
    }
    client = SharePointLookupClient(
        "https://example.test/lookup",
        1.0,
        transport=lambda request, timeout: HttpResponse(
            200,
            json.dumps(payload).encode("utf-8"),
        ),
    )
    summary = TagLookupSessionSummary()

    result = client.lookup("AAA1")

    assert result.status is TagLookupStatus.NOT_FOUND
    assert not summary.update(result)
    assert summary.total == 0
