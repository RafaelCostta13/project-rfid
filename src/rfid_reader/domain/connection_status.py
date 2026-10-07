"""Estados de conexão independentes de infraestrutura e interface."""

from enum import StrEnum


class ConnectionKind(StrEnum):
    """Conexões apresentadas na tela principal."""

    RFID = "rfid"
    INTERNET = "internet"
    WAVESHARE = "waveshare"
    DATABASE = "database"
    SYSTEM = "system"
    SYNC = "sync"


class ConnectionStatus(StrEnum):
    """Estados visuais possíveis para uma conexão."""

    CHECKING = "Verificando"
    CONNECTED = "Conectado"
    DISCONNECTED = "Desconectado"
    ERROR = "Erro"
