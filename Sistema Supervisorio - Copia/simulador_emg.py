import serial
import time
import math
import random

# Conecta na porta PAR da COM3 (Ex: COM4 pareada com a COM3)
PORTA_SIMULADOR = "COM1"
BAUDRATE = 115200

def gerar_amostra_emg(tempo_atual):
    """
    Gera um sinal EMG sintético:
    - Ruído de fundo (linha de base em repouso)
    - Surtos de contração muscular a cada 3 segundos
    """
    linha_base = 512
    ruido_repouso = random.gauss(0, 12)
    
    # Ciclo de contração: dura 1.2s a cada 3.0s
    periodo_ciclo = 3.0
    duracao_contracao = 1.2
    fase = tempo_atual % periodo_ciclo
    
    if fase < duracao_contracao:
        # Modulação de envelope suave (senoidal) para a contração
        envelope = math.sin(math.pi * (fase / duracao_contracao))
        sinal_ativo = random.gauss(0, 220) * envelope
    else:
        sinal_ativo = 0

    valor_final = linha_base + ruido_repouso + sinal_ativo
    return int(max(0, min(1023, valor_final)))

def executar_simulacao():
    try:
        ser = serial.Serial(PORTA_SIMULADOR, BAUDRATE, timeout=1)
        print(f"[SIMULADOR EMG] Transmitindo em {PORTA_SIMULADOR} a {BAUDRATE} baud...")
        
        t0 = time.time()
        while True:
            t = time.time() - t0
            valor = gerar_amostra_emg(t)
            
            # Formato esperado pelo supervisório: valor inteiro + quebra de linha
            dados = f"{valor}\n".encode('utf-8')
            ser.write(dados)
            
            # Envia a cada 5ms (~200 Hz) para coincidir com o loop do supervisório
            time.sleep(0.005)

    except serial.SerialException as e:
        print(f"Erro ao abrir {PORTA_SIMULADOR}: {e}")
        print("Certifique-se de que o par de portas virtuais (COM3 <-> COM4) está ativo.")
    except KeyboardInterrupt:
        print("\nSimulação encerrada pelo usuário.")
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    executar_simulacao()