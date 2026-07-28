from sllurp.llrp import LLRPReaderClient, LLRPReaderConfig

READER_IP = "192.168.0.214"

config = LLRPReaderConfig({})

reader = LLRPReaderClient(READER_IP, config=config)

print("Conectando...")

reader.connect()

print("Conectado com sucesso!")

reader.disconnect()

print("Desconectado.")
