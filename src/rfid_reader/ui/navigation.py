"""Estado de navegação independente dos widgets da interface."""

from dataclasses import dataclass
from enum import StrEnum


class PageId(StrEnum):
    """Páginas disponíveis no menu principal."""

    SYSTEM_STATUS = "system_status"
    RFID_SETTINGS = "rfid_settings"
    WAVESHARE_DIAGNOSTIC = "waveshare_diagnostic"


@dataclass(slots=True)
class NavigationState:
    """Mantém a página selecionada sem conhecer a implementação visual."""

    current_page: PageId = PageId.SYSTEM_STATUS

    def select(self, page: PageId) -> bool:
        """Seleciona uma página e informa se houve mudança."""

        if page is self.current_page:
            return False
        self.current_page = page
        return True
