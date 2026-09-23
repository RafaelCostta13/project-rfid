import time

from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

PORT = "COM5"
BAUDRATE = 9600
DEVICE_ID = 1

POLL_INTERVAL = 0.05
TIMER_LIMIT = 30.0


# ==========================================================
# ENTRADAS DIGITAIS
# ==========================================================

DI1 = 0  # Sensor de entrada
DI2 = 1  # Sensor de saída


# ==========================================================
# RELÉS
# ==========================================================

CH1 = 0  # Dois sensores ativos
CH2 = 1  # Leitura RFID / Timer ativo
CH3 = 2  # Dois sensores desativados


# ==========================================================
# CLIENTE MODBUS
# ==========================================================

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=2,
)


# ==========================================================
# FUNÇÕES
# ==========================================================

def set_relay(address: int, ligado: bool) -> bool:
    """
    Liga ou desliga um relé.

    CH1 = address 0
    CH2 = address 1
    CH3 = address 2
    """

    resultado = client.write_coil(
        address=address,
        value=ligado,
        device_id=DEVICE_ID,
    )

    if resultado.isError():
        print(
            f"\nERRO ao controlar CH{address + 1}: "
            f"{resultado}"
        )
        return False

    return True


def read_sensors():
    """
    Lê DI1 e DI2.

    True  = Sensor ativo
    False = Sensor desativado/interrompido
    """

    resultado = client.read_discrete_inputs(
        address=0,
        count=2,
        device_id=DEVICE_ID,
    )

    if resultado.isError():
        print("\nERRO na leitura dos sensores:", resultado)
        return None

    di1 = resultado.bits[DI1]
    di2 = resultado.bits[DI2]

    return di1, di2


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

def main():

    print("=" * 65)
    print("SISTEMA DE TESTE - SENSORES + RELÉS + TIMER RFID")
    print("=" * 65)

    print()
    print(f"Porta: {PORT}")
    print(f"Baudrate: {BAUDRATE}")
    print(f"Device ID: {DEVICE_ID}")

    print()
    print("ENTRADAS:")
    print("  DI1 = Sensor de entrada")
    print("  DI2 = Sensor de saída")

    print()
    print("SAÍDAS:")
    print("  CH1 = Dois sensores ativos")
    print("  CH2 = Leitura RFID / Timer ativo")
    print("  CH3 = Dois sensores desativados")

    print()
    print(f"Tempo máximo de leitura: {TIMER_LIMIT:.0f} segundos")
    print("Pressione Ctrl+C para encerrar.")

    print()
    print("=" * 65)

    # ======================================================
    # CONEXÃO
    # ======================================================

    if not client.connect():
        print(f"ERRO: Não foi possível abrir {PORT}")
        return

    print()
    print(f"Conectado com sucesso em {PORT}.")

    # ======================================================
    # ESTADO DO TIMER
    # ======================================================

    timer_ativo = False
    inicio_timer = None

    # ======================================================
    # ESTADO DOS RELÉS
    # ======================================================

    estado_anterior_ch1 = None
    estado_anterior_ch2 = None
    estado_anterior_ch3 = None

    try:

        # ==================================================
        # LEITURA INICIAL
        # ==================================================

        sensores = read_sensors()

        if sensores is None:
            print("Não foi possível realizar a leitura inicial.")
            return

        estado_anterior_di1, estado_anterior_di2 = sensores

        print()
        print("Estado inicial:")

        print(
            f"DI1 = "
            f"{'ON' if estado_anterior_di1 else 'OFF'}"
        )

        print(
            f"DI2 = "
            f"{'ON' if estado_anterior_di2 else 'OFF'}"
        )

        print()

        # ==================================================
        # LOOP PRINCIPAL
        # ==================================================

        while True:

            # ==============================================
            # LEITURA DOS SENSORES
            # ==============================================

            sensores = read_sensors()

            if sensores is None:
                time.sleep(1)
                continue

            di1, di2 = sensores

            # ==============================================
            # DETECÇÃO DE MUDANÇA DOS SENSORES
            # ==============================================

            if di1 != estado_anterior_di1:

                print()

                print(
                    f">>> DI1 mudou: "
                    f"{'ON' if estado_anterior_di1 else 'OFF'}"
                    f" -> "
                    f"{'ON' if di1 else 'OFF'}"
                )

            if di2 != estado_anterior_di2:

                print()

                print(
                    f">>> DI2 mudou: "
                    f"{'ON' if estado_anterior_di2 else 'OFF'}"
                    f" -> "
                    f"{'ON' if di2 else 'OFF'}"
                )

            # ==============================================
            # DETECÇÃO DE BORDA ON -> OFF
            # ==============================================

            entrada_desativada = (
                estado_anterior_di1
                and not di1
            )

            saida_desativada = (
                estado_anterior_di2
                and not di2
            )

            # ==============================================
            # DI1 - SENSOR DE ENTRADA
            # ==============================================

            if entrada_desativada:

                print()
                print("=" * 65)
                print("SENSOR DE ENTRADA DESATIVADO")
                print("DI1: ON -> OFF")

                # Inicia somente se não houver timer ativo
                if not timer_ativo:

                    inicio_timer = time.monotonic()
                    timer_ativo = True

                    print()
                    print(">>> TIMER INICIADO")
                    print(">>> LEITURA RFID INICIADA")

                else:

                    print()
                    print(">>> Timer já estava ativo.")

                print("=" * 65)

            # ==============================================
            # DI2 - SENSOR DE SAÍDA
            # ==============================================

            if saida_desativada:

                print()
                print("=" * 65)
                print("SENSOR DE SAÍDA DESATIVADO")
                print("DI2: ON -> OFF")

                # Finaliza timer se estiver ativo
                if timer_ativo and inicio_timer is not None:

                    tempo_decorrido = (
                        time.monotonic()
                        - inicio_timer
                    )

                    timer_ativo = False
                    inicio_timer = None

                    print()
                    print(
                        f">>> TIMER FINALIZADO EM "
                        f"{tempo_decorrido:.2f} segundos"
                    )

                    print(">>> LEITURA RFID FINALIZADA")

                else:

                    print()
                    print(">>> Nenhum timer estava ativo.")

                print("=" * 65)

            # ==============================================
            # TIMEOUT DO TIMER
            # ==============================================

            if timer_ativo and inicio_timer is not None:

                tempo_decorrido = (
                    time.monotonic()
                    - inicio_timer
                )

                print(
                    f"\rLEITURA RFID ATIVA | "
                    f"{tempo_decorrido:05.1f} / "
                    f"{TIMER_LIMIT:.0f}s",
                    end="",
                    flush=True,
                )

                if tempo_decorrido >= TIMER_LIMIT:

                    print()
                    print()
                    print("=" * 65)
                    print("TIMEOUT DA LEITURA RFID")

                    timer_ativo = False
                    inicio_timer = None

                    print()
                    print(
                        f">>> LIMITE DE "
                        f"{TIMER_LIMIT:.0f} SEGUNDOS ATINGIDO"
                    )

                    print(">>> TIMER FINALIZADO")
                    print(">>> LEITURA RFID FINALIZADA")

                    print("=" * 65)

            # ==============================================
            # LÓGICA DOS RELÉS
            # ==============================================
            #
            # PRIORIDADE 1
            #
            # DI1 OFF + DI2 OFF
            #
            # CH1 = OFF
            # CH2 = OFF
            # CH3 = ON
            #
            # ----------------------------------------------
            #
            # PRIORIDADE 2
            #
            # Timer ativo
            #
            # CH1 = OFF
            # CH2 = ON
            # CH3 = OFF
            #
            # ----------------------------------------------
            #
            # PRIORIDADE 3
            #
            # DI1 ON + DI2 ON
            #
            # CH1 = ON
            # CH2 = OFF
            # CH3 = OFF
            #
            # ----------------------------------------------
            #
            # Outros estados:
            #
            # todos OFF
            #
            # ==============================================

            if not di1 and not di2:

                # Ambos sensores desativados
                ch1_desejado = False
                ch2_desejado = False
                ch3_desejado = True

            elif timer_ativo:

                # Leitura RFID em andamento
                ch1_desejado = False
                ch2_desejado = True
                ch3_desejado = False

            elif di1 and di2:

                # Ambos sensores ativos
                ch1_desejado = True
                ch2_desejado = False
                ch3_desejado = False

            else:

                # Estado intermediário não previsto
                ch1_desejado = False
                ch2_desejado = False
                ch3_desejado = False

            # ==============================================
            # ATUALIZA CH1
            # ==============================================

            if ch1_desejado != estado_anterior_ch1:

                if set_relay(CH1, ch1_desejado):

                    estado_anterior_ch1 = ch1_desejado

                    print(
                        f"\n>>> CH1 "
                        f"{'LIGADO' if ch1_desejado else 'DESLIGADO'}"
                    )

            # ==============================================
            # ATUALIZA CH2
            # ==============================================

            if ch2_desejado != estado_anterior_ch2:

                if set_relay(CH2, ch2_desejado):

                    estado_anterior_ch2 = ch2_desejado

                    if ch2_desejado:

                        print(
                            ">>> CH2 LIGADO "
                            "- LEITURA RFID"
                        )

                    else:

                        print(
                            ">>> CH2 DESLIGADO"
                        )

            # ==============================================
            # ATUALIZA CH3
            # ==============================================

            if ch3_desejado != estado_anterior_ch3:

                if set_relay(CH3, ch3_desejado):

                    estado_anterior_ch3 = ch3_desejado

                    if ch3_desejado:

                        print(
                            ">>> CH3 LIGADO "
                            "- DOIS SENSORES DESATIVADOS"
                        )

                    else:

                        print(
                            ">>> CH3 DESLIGADO"
                        )

            # ==============================================
            # ATUALIZA ESTADO ANTERIOR
            # ==============================================

            estado_anterior_di1 = di1
            estado_anterior_di2 = di2

            # ==============================================
            # INTERVALO
            # ==============================================

            time.sleep(POLL_INTERVAL)

    # ======================================================
    # CTRL + C
    # ======================================================

    except KeyboardInterrupt:

        print()
        print()
        print("=" * 65)
        print("Programa encerrado pelo usuário.")
        print("=" * 65)

    # ======================================================
    # ERRO MODBUS
    # ======================================================

    except ModbusException as erro:

        print()
        print(f"Erro de comunicação Modbus: {erro}")

    # ======================================================
    # FINALIZAÇÃO
    # ======================================================

    finally:

        print()
        print("Desligando todos os relés...")

        try:

            set_relay(CH1, False)
            set_relay(CH2, False)
            set_relay(CH3, False)

            print("CH1 desligado.")
            print("CH2 desligado.")
            print("CH3 desligado.")

        except ModbusException as erro:

            print(
                f"Erro ao desligar relés: {erro}"
            )

        client.close()

        print()
        print(f"{PORT} fechada.")
        print("Programa finalizado.")


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":
    main()