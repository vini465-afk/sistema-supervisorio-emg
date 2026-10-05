# =========================================================
# BIBLIOTECAS
# =========================================================

# Bibliotecas Tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

# Biblioteca matplotlib que faz o Tkinter entender o gráfico
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Biblioteca para controlar o tempo
import time

# Biblioteca do PySerial
import serial

# Geração do sinal EMG simulado
import math
import random


# =========================================================
# BLOCO DE FUNÇÕES
# =========================================================

# Função para criar a janela do Label
def criar_janelatk():

    Janela2 = Toplevel(janela)

    Janela2.title("Label")
    Janela2.geometry("400x300")


# =========================================================
# FUNÇÃO PARA INICIAR/PARAR A GRAVAÇÃO
# =========================================================

def iniciar_gravacao():

    global gravando
    global dados_gravacao
    global tempo_inicio

    if gravando == False:

        gravando = True

        # Limpa os dados da gravação anterior
        dados_gravacao = []

        # Guarda o momento em que a gravação começou
        tempo_inicio = time.time()

        print("Gravação iniciada")

        # Depois de 30 segundos chama finalizar_gravacao
        janela.after(30000, finalizar_gravacao)

    else:

        gravando = False

        print("Gravação encerrada manualmente")

        salvar_dados()


# =========================================================
# FUNÇÃO QUE FINALIZA A GRAVAÇÃO APÓS 30 SEGUNDOS
# =========================================================

def finalizar_gravacao():

    global gravando

    if gravando:

        gravando = False

        print("Gravação encerrada após 30 segundos")

        salvar_dados()


# =========================================================
# FUNÇÃO PARA SALVAR OS DADOS
# =========================================================

def salvar_dados():

    if len(dados_gravacao) == 0:

        print("Nenhum dado para salvar.")

        return


    # Abre a janela para escolher onde salvar
    arquivo = filedialog.asksaveasfilename(

        title="Salvar gravação",

        defaultextension=".csv",

        filetypes=[
            ("Arquivo CSV", "*.csv"),
            ("Todos os arquivos", "*.*")
        ]
    )


    # Se o usuário cancelar
    if arquivo == "":

        print("Salvamento cancelado.")

        return


    # Cria/abre o arquivo
    with open(arquivo, "w", encoding="utf-8") as f:

        # Cabeçalho
        f.write("Tempo,Valor EMG\n")


        # Percorre os dados gravados
        for tempo, valor in dados_gravacao:

            f.write(f"{tempo:.3f},{valor}\n")


    print("Gravação salva!")


# =========================================================
# SIMULAÇÃO DO SINAL EMG (CONTRAÇÃO / RELAXAMENTO)
# =========================================================
# Modelo em ADC 10 bits (0–1023), linha de base ~512:
# - Relaxamento: ruído de fundo de baixa amplitude
# - Contração: interferência de alta amplitude com ataque,
#   platô e decaimento (envelope típico de EMG de superfície)

EMG_BASELINE = 512
EMG_ADC_MIN = 1280
EMG_ADC_MAX = 1848
EMG_CICLO_S = 2.0
EMG_CONTRACAO_S = 2.5
EMG_ATAQUE_S = 0.20
EMG_DECAIMENTO_S = 0.30
EMG_RUIDO_REPOUSO = 80
EMG_AMPLITUDE_CONTRACAO = 500

tempo_inicio_simulacao = time.time()


def envelope_contracao(fase):

    if fase >= EMG_CONTRACAO_S:

        return 0.0

    if fase < EMG_ATAQUE_S:

        t = fase / EMG_ATAQUE_S

        return t * t * (3.0 - 2.0 * t)

    restante = EMG_CONTRACAO_S - fase

    if restante < EMG_DECAIMENTO_S:

        t = restante / EMG_DECAIMENTO_S

        return t * t * (3.0 - 2.0 * t)

    # Pequena variação de força no platô
    return 0.88 + 0.12 * math.sin(2.0 * math.pi * 7.0 * fase)


def gerar_amostra_emg(tempo_atual):

    fase = tempo_atual % EMG_CICLO_S
    env = envelope_contracao(fase)

    ruido_repouso = random.gauss(0.0, EMG_RUIDO_REPOUSO)
    interferencia = random.gauss(0.0, EMG_AMPLITUDE_CONTRACAO) * env

    if env > 0.0:

        interferencia += env * 18.0 * math.sin(2.0 * math.pi * 50.0 * tempo_atual)
        interferencia += env * 10.0 * math.sin(2.0 * math.pi * 87.0 * tempo_atual)

    valor = EMG_BASELINE + ruido_repouso + interferencia
    valor_adc = int(max(EMG_ADC_MIN, min(EMG_ADC_MAX, round(valor))))
    em_contracao = env > 0.12

    return valor_adc, em_contracao


# =========================================================
# CONEXÃO COM A PORTA SERIAL
# =========================================================

try:

    ser = serial.Serial(

        port="COM4",

        baudrate=115200,

        timeout=0.1
    )

    print("Serial conectada com sucesso!")


except serial.SerialException:

    ser = None

    print("Nenhuma porta serial encontrada.")


# Esta cópia prioriza a simulação do EMG (contração/relaxamento).
# Para usar apenas a serial real, altere para False.
FORCAR_SIMULACAO_EMG = True

if FORCAR_SIMULACAO_EMG:

    print("Modo simulação EMG ativo (contração e relaxamento).")



# =========================================================
# JANELA PRINCIPAL
# =========================================================

janela = Tk()

janela.title("Sistema Supervisorio")

janela.geometry("900x600")


# =========================================================
# STATUS DA PORTA SERIAL
# =========================================================

status_serial = StringVar()


if FORCAR_SIMULACAO_EMG or ser is None:

    status_serial.set("● Fonte: Simulação EMG")

else:

    status_serial.set("● Serial: Conectada")



status_emg = StringVar()

status_emg.set("Estado EMG: Relaxamento")


ttk.Label(

    janela,

    textvariable=status_serial

).grid(

    row=2,

    column=0,

    columnspan=4,

    pady=2
)


ttk.Label(

    janela,

    textvariable=status_emg

).grid(

    row=3,

    column=0,

    columnspan=4,

    pady=2
)


# =========================================================
# CONFIGURAÇÃO DAS LINHAS
# =========================================================

janela.rowconfigure(

    0,

    weight=1
)


janela.rowconfigure(

    1,

    weight=0
)


# =========================================================
# CONFIGURAÇÃO DAS COLUNAS
# =========================================================

janela.columnconfigure(

    0,

    weight=1
)


janela.columnconfigure(

    1,

    weight=1
)


janela.columnconfigure(

    2,

    weight=1
)


janela.columnconfigure(

    3,

    weight=1
)


# =========================================================
# DADOS DO GRÁFICO / VARREDURA
# =========================================================

x = []

y = []


# Contador das amostras
contador = 0


# Quantidade máxima de pontos
# que ficarão visíveis no gráfico
MAX_PONTOS = 1500

PONTOS_VISIVEIS = 1500

escala_y_max = EMG_ADC_MAX

texto_escala = StringVar()

texto_escala.set(str(escala_y_max))


# =========================================================
# VARIÁVEIS DA GRAVAÇÃO
# =========================================================

gravando = False

dados_gravacao = []

tempo_inicio = 0


# =========================================================
# CRIAÇÃO DO GRÁFICO
# =========================================================

fig = Figure(

    figsize=(6, 4),

    dpi=100
)


ax = fig.add_subplot()


# Cria uma linha inicialmente vazia
linha, = ax.plot(

    [],

    []
)


ax.set_title(

    "Grafico EMG"
)


ax.set_xlabel(

    "Amostras"
)


ax.set_ylabel(

    "Amplitude"
)


# =========================================================
# CONFIGURAÇÃO INICIAL DA VARREDURA
# =========================================================

# Define o tamanho inicial da janela horizontal
ax.set_xlim(

    0,

    MAX_PONTOS
)


ax.set_ylim(

    EMG_ADC_MIN,

    EMG_ADC_MAX
)


# =========================================================
# COLOCANDO O GRÁFICO NA INTERFACE
# =========================================================

canvas = FigureCanvasTkAgg(

    fig,

    master=janela
)


canvas.draw()


canvas.get_tk_widget().grid(

    row=0,

    column=0,

    columnspan=4,

    sticky="nsew"
)


# =========================================================
# ESCALA DO GRÁFICO (CAIXA DE TEXTO)
# =========================================================

def aplicar_escala(event=None):

    global escala_y_max

    texto = texto_escala.get().strip().replace(",", ".")

    try:

        nova_escala = float(texto)

    except ValueError:

        print("Escala inválida. Digite um número, por exemplo 4590.")
        texto_escala.set(str(int(escala_y_max) if escala_y_max == int(escala_y_max) else escala_y_max))
        return

    if nova_escala <= 0:

        print("A escala deve ser maior que zero.")
        return

    escala_y_max = nova_escala
    ax.set_ylim(0, escala_y_max)
    canvas.draw_idle()
    print(f"Escala do gráfico: 0 a {escala_y_max}")


# =========================================================
# FUNÇÃO QUE RECEBE OS DADOS DA SERIAL
# =========================================================

def processar_amostra(valor, em_contracao=None):

    global contador

    global gravando

    global dados_gravacao

    global tempo_inicio


    contador += 1

    x.append(contador)

    y.append(valor)


    if len(x) > MAX_PONTOS:

        x.pop(0)

        y.pop(0)


    xs = x[-PONTOS_VISIVEIS:]
    ys = y[-PONTOS_VISIVEIS:]

    linha.set_data(

        xs,

        ys
    )


    if em_contracao is True:

        linha.set_color("tab:red")

        status_emg.set("Estado EMG: Contração")

    elif em_contracao is False:

        linha.set_color("tab:blue")

        status_emg.set("Estado EMG: Relaxamento")


    if contador < PONTOS_VISIVEIS:

        ax.set_xlim(

            0,

            PONTOS_VISIVEIS
        )

    else:

        ax.set_xlim(

            xs[0],

            contador + 1
        )


    if contador % 4 == 0:

        canvas.draw_idle()


    if gravando:

        tempo_decorrido = (

            time.time()
            -
            tempo_inicio
        )

        dados_gravacao.append(

            [
                tempo_decorrido,

                valor
            ]
        )


def atualizar():

    amostra_ok = False
    valor = None
    em_contracao = None


    if FORCAR_SIMULACAO_EMG or ser is None:

        tempo_atual = time.time() - tempo_inicio_simulacao
        valor, em_contracao = gerar_amostra_emg(tempo_atual)
        amostra_ok = True

    elif ser.in_waiting > 0:

        try:

            linha_serial = ser.readline().decode(
                "utf-8"
            ).strip()

            if linha_serial != "":

                valor = int(linha_serial)
                amostra_ok = True

        except ValueError:

            pass


    if amostra_ok:

        processar_amostra(valor, em_contracao)


    janela.after(

        5,

        atualizar
    )


# =========================================================
# BOTÃO GRAVAR
# =========================================================

ttk.Button(

    janela,

    text="Gravar",

    command=iniciar_gravacao

).grid(

    row=1,

    column=0,

    sticky="sw",

    padx=20,

    pady=20
)


# =========================================================
# BOTÃO SALVAR
# =========================================================

ttk.Button(

    janela,

    text="Salvar",

    command=salvar_dados

).grid(

    row=1,

    column=1,

    sticky="s",

    padx=20,

    pady=20
)


# =========================================================
# CAIXA DE TEXTO DA ESCALA
# =========================================================

frame_escala = ttk.Frame(janela)

frame_escala.grid(

    row=1,

    column=2,

    sticky="s",

    padx=10,

    pady=16
)

ttk.Label(

    frame_escala,

    text="Escala Y:"

).pack(side="left", padx=(0, 6))

entrada_escala = ttk.Entry(

    frame_escala,

    textvariable=texto_escala,

    width=10

)

entrada_escala.pack(side="left")

entrada_escala.bind("<Return>", aplicar_escala)

ttk.Button(

    frame_escala,

    text="Aplicar",

    command=aplicar_escala

).pack(side="left", padx=(6, 0))


# =========================================================
# BOTÃO LABEL
# =========================================================

ttk.Button(

    janela,

    text="Label",

    command=criar_janelatk

).grid(

    row=1,

    column=3,

    sticky="se",

    padx=20,

    pady=20
)


# =========================================================
# INICIA A LEITURA DA SERIAL
# =========================================================

atualizar()


# =========================================================
# EXECUTA O PROGRAMA
# =========================================================

janela.mainloop()


# =========================================================
# FECHA A PORTA SERIAL AO ENCERRAR
# =========================================================

if ser is not None:

    ser.close()