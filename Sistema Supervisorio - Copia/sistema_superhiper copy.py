# 1 - IMPORTAÇÃO DE BIBLIOTECAS (Dependências)

# 1.1 - Bibliotecas Tkinter: Interface Gráfica padrão do Python
# 1.2 - permite importar a interface grafica do tkinter
from tkinter import *
# 1.3 - tkk deixa a interface mais moderna 
from tkinter import ttk
# 1.4 - filedialog cria janelas para o usuario manipular diferentes arquvios
from tkinter import filedialog

# 2 - Bibliotecas Matplotlib: Criação do gráfico e integração com o Tkinter
# 2.1 - figurecanvastkagg faz a ponte entre o matplotlib e o tkinter fazendo com que o grafico seja criando dentro da janela do tkinter 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# 2.2 - figure e usado para criar uma area onde o grafico é criado
from matplotlib.figure import Figure

# 3 - Biblioteca nativa para capturar timestamps (tempo decorrido)
# 3.1 permite trabalhar com tempo (Vai ser usado no CSV)
import time

# 4 - Biblioteca PySerial: Comunicação com a porta USB/Serial (No nosso caso RaspBerry)
# 4.1 - permite que o sistema converse com dispositivos atraves da USB (Usado para receber os dados EMG do RaspBerry )
import serial

# 5 - Biblioteca OS: Manipulação de caminhos de arquivos e pastas no sistema operacional
# 5.1 - permite trabalhar com recursos operacionais como pastas arquivos e caminhos
import os


# 6 -FUNÇÕES DE CONTROLE DA INTERFACE E DADOS

# 6.1 - Cria um bloco de função que se chama criar janelatkk (def significa função)
def criar_janelatk():
    """Cria uma janela secundária para futura configuração de Labels (rótulos de dados).""" #So pra explicar oq a função faz 
    # 6.2 -Toplevel cria uma nova janela "filha" vinculada a janela principal
    Janela2 = Toplevel(janela)
    # 6.3 - fala que o nome da janela é "Label"
    Janela2.title("Label")
    # 6.4 - Fala o tamanho da janela em px 
    Janela2.geometry("400x300")

# 7 - bloco de gravao do CSV 
def iniciar_gravacao():
    """Inicia ou interrompe manualmente a gravação dos dados lidos da serial."""
    global gravando
    global dados_gravacao # 7.1 - Permite que a função altere o valor dessas variaveis 
    global tempo_inicio

    # 7.2 - Aqui o programa pergunta se a variavel GRAVANDO é verdadeira ou falsa. Se for falsa ela faz o seguinte comando:
    if gravando == False:
        # 7.3 - Muda o estado para iniciar a captura de dados
        gravando = True ## Pensei como se fosse um botão (e realmente ele é um), se fosse aceionado ele seria verdadeiro, se não precionado seria falso
        
        # 7.4 - Apaga os dados da gravacao anterior e cria uma lista, isso evita que os dados das gravacoes se misturem
        dados_gravacao = []
        
        # 7.5 - Marca o tempo exato de início (timestamp inicial) para calcular o tempo relativo depois
        tempo_inicio = time.time() ##Basicamente esse "time.time" pega o tempo do pc com referencia interna Unix Epoch 
        # 7.6 - Vai aparecer essa mensagem no TERMINAL e nao na janela principal 
        print("Gravação iniciada")
        
        # 7.7 - after manda o tkinter realizar tal funcao que no caso é para parar a gravao depois de 30000 mile segundos (30 segundos). Então, depois de 30 segndos finalizar_gravacao e exacutada 
        janela.after(30000, finalizar_gravacao)
    else: # Se não
        # 7.8 - Se já estiver gravando e o botão for clicado, interrompe a gravação
        gravando = False
        # 7.9 - Essa mensagem vai aparecer no terminal
        print("Gravação encerrada manualmente")
        # 7.1.1 - Chama a função para salvar o que foi capturado até o momento
        salvar_dados()

# 8 - cria a funcao de finalizar a gravacao
def finalizar_gravacao():
    """Encerra a gravação automaticamente após o tempo limite (30s) acabar."""
    # 8.1 - Permirte alterar a variavel global gravando
    global gravando
    # 8.2 - forma simples de dizer que gravando e verdadeiro
    if gravando:
        # 8.3 - se gravando por verdadeiro vai rodar o seguinte bloco:
        gravando = False
        # 8.4 - Essa mensagem ira aparecer no terminal
        print("Gravação encerrada após 30 segundos")
        # 8.5 - Salva todos os dados que foi capturado ate o momento na funcao "salvar_dados"
        salvar_dados()

# 9 - Cria a funcao responsavel por salvar os dados no CSV
def salvar_dados():
    """Pega os dados armazenados na memória RAM e escreve em um arquivo CSV."""
    # 9.1 - len verifique quantos elementos existem na lista
    if len(dados_gravacao) == 0:
        # 9.2 - Se existir 0 elementos na lista e exibida a seguinte mensagem
        print("Nenhum dado para salvar.") ## Evita de criar arquivos que nao tem nada 
        # 9.2 - return encerra a funcao IMEDIATAMENTE, ou seja a funcao nao fica tentando criar o arquivo
        return

    # 10 - Descobre a pasta onde este script Python está salvo atualmente
    # 10.1 - "__file__" representa o proprio caminho em que o arquivo esta sendo executado (No caso dentro da pasta sistema supervisorio)
    # 10.1.(2) - "os.path.abspath" transforma esse caminho em um caminho absoluto, ou seja, o arquivo csv so vai ser salvo na mesma pasta que o supervisorio esta sendo rodado 
    # 10.1.(3) - "os.path.dirname" pega somente a pasta em que o sistema supervisorio esta sendo executado, exemplo:
    # F:\ETEC\TCC\sistema supervisorio\ superhiper.py se torna ---> F:\ETEC\TCC\sistema supervisorio
    pasta = os.path.dirname(os.path.abspath(__file__))
    # 10.2 - Cria o caminho completo para o arquivo "1_DADOS.csv" nesta mesma pasta
    arquivo = os.path.join(pasta, "1_DADOS.csv")

    # 11 - Abre (ou cria) o arquivo em modo de escrita ("w" - write) com codificação UTF-8 (escrever os caracteres) e cria uma variavel f que representa o arquivo aberto 
    with open(arquivo, "w", encoding="utf-8") as f:
        # 11.1 - Escreve o cabeçalho do arquivo CSV. "\n" representa a quebra de linha apos os dados na respectiva ordem foi criado
        f.write("timestamp,valor,label\n")
        
        # 11.2 - Aqui onde comeca o loop, ele pega todos os dados gravados em "dados_gracacao" e pega os tres valores
        for tempo, valor, label in dados_gravacao:
            # 11.3 - Escreve cada linha separando os valores por vírgula e pulando linha (\n)
            f.write(f"{tempo},{valor},{label}\n")

    # 11.4 - mostra no terminal que o arquivo foi salvo
    print("Gravação salva em 1_DADOS.csv")


# 12 - CONFIGURAÇÃO DA CONEXÃO SERIAL

try: # 12.1 - comeca o bloco de tentativa
    # 12.2 - Tenta abrir a porta COM4 com velocidade de 115200 bits por segundo (baudrate)
    # 12.3 - timeout=0.1 evita que o programa trave infinitamente esperando um dado
    ser = serial.Serial(port="COM4", baudrate=115200, timeout=0.1)
    # 12.4 - se estiver tudo ok aparecera essa mensagem no terminal
    print("Serial conectada com sucesso!")
except serial.SerialException: # 12.5 - se acontecer algum erro especifico com a serial sera executado esse bloco
    # 12.5 - Se a porta COM4 não existir ou estiver em uso, captura o erro para o app não "crashar"
    ser = None ## None significa nesse contexto que a conexao serial nao existe 
    print("Nenhuma porta serial encontrada.")



# 13 - CONFIGURAÇÃO DA JANELA PRINCIPAL (TKINTER)
# 13.1 - cria uma janela principal no tkinter 
janela = Tk()
# 13.2 - Define o nome dessa janela principal como "sistema supervisorio"
janela.title("Sistema Supervisorio")
# 13.3 - define op tamanhpo inicial dessa janela em px (800 de largura x 600 de altura )
janela.geometry("800x600")

# 14 - Variável atrelada ao Tkinter que será atualizada dinamicamente na tela
status_serial = StringVar()

# 14.1 - Define o texto inicial com base no sucesso da conexão serial
if ser is None: #14.2 - verifica se a conexao nao existe. Se "ser = None" ent nao existe conexao
    status_serial.set("● Serial: Desconectada")
else: #14.3 - Se a conexao existir vai aparecer essa mensagem no terminal 
    status_serial.set("● Serial: Conectada")

# 15 - "tkk.lbel" cria um texto na inteface "janela" indica que o label pertence a janela principal "textvariable=status_serial" faz o label mostrar o conteudo de "status_serail"
# ".grid" posiciona o texto por um sistema de grades do tkinter
ttk.Label(janela, textvariable=status_serial).grid(row=2, column=0, columnspan=3, pady=5)
# "row=2" coloca na linha 2. "column=0" comeca na coluna 0. "columspan=3" faz o label ocupar 3 colunas. "pady=5" adiciona um espaco vertical de 5 px

# 16 - Configura o peso de redimensionamento das linhas e colunas (responsividade da janela)
janela.rowconfigure(0, weight=1)  # 16.1 - 'weight=1' Linha do gráfico expande
janela.rowconfigure(1, weight=0)  # 16.2 - "weight=0" Linha dos botões fica fixa
janela.columnconfigure(0, weight=1)
janela.columnconfigure(1, weight=1)
janela.columnconfigure(2, weight=1)


# VARIÁVEIS GLOBAIS DE ESTADO E GRÁFICO

x = [] # Eixo X (Amostras)
y = [] # Eixo Y (Valores de Amplitude)
contador = 0
MAX_PONTOS = 1500 # Tamanho máximo da "janela deslizante" do gráfico

gravando = False
dados_gravacao = []
tempo_inicio = 0
label_atual = 1


# CONFIGURAÇÃO DO GRÁFICO (MATPLOTLIB)

# Cria a figura (container) do Matplotlib
fig = Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot()

# Inicializa uma linha vazia que será atualizada iterativamente para melhor performance
linha, = ax.plot([], [])
ax.set_title("Grafico EMG")
ax.set_xlabel("Amostras")
ax.set_ylabel("Amplitude")

# Define os limites iniciais do eixo X (0 até 1500 amostras)
ax.set_xlim(0, MAX_PONTOS)

# Conecta a figura do Matplotlib ao Tkinter (renderiza no Canvas)
canvas = FigureCanvasTkAgg(fig, master=janela)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, columnspan=3, sticky="nsew")


# LOOP PRINCIPAL DE AQUISIÇÃO (WORKER)

def atualizar():
    """Função recursiva que roda continuamente verificando dados novos na porta serial."""
    global contador, gravando, dados_gravacao, tempo_inicio

    if ser is not None:
        # Verifica se há bytes disponíveis no buffer da serial
        if ser.in_waiting > 0:
            try:
                # Lê a linha crua, decodifica para texto (utf-8) e remove quebras de linha/espaços (.strip())
                linha_serial = ser.readline().decode("utf-8").strip()

                if linha_serial != "":
                    # Converte o texto recebido para número inteiro
                    valor = int(linha_serial)
                    contador += 1
                    
                    # Alimenta as listas de eixos X e Y
                    x.append(contador)
                    y.append(valor)

                    # Se a quantidade de dados ultrapassar o limite, remove o dado mais antigo (índice 0)
                    if len(x) > MAX_PONTOS:
                        x.pop(0)
                        y.pop(0)

                    # Injeta os novos dados na linha do gráfico
                    linha.set_data(x, y)

                    # Ajuste do Eixo X: Comportamento de janela deslizante
                    if contador < MAX_PONTOS:
                        ax.set_xlim(0, MAX_PONTOS)
                    else:
                        # Gráfico cheio: desliza a visualização junto com a amostra mais recente
                        ax.set_xlim(contador - MAX_PONTOS + 1, contador + 1)

                    # Reajusta a escala do Eixo Y automaticamente baseado nos valores de Y atuais
                    ax.relim()
                    ax.autoscale_view(scalex=False, scaley=True)

                    # Redesenha o gráfico na interface otimizando para uso em tempo real
                    canvas.draw_idle()

                    # Rotina de Gravação de Dados na Memória (se ativada)
                    if gravando:
                        # Calcula a diferença entre o momento atual e quando o botão gravar foi clicado
                        tempo_decorrido = time.time() - tempo_inicio
                        # Salva na memória RAM o registro deste instante
                        dados_gravacao.append([tempo_decorrido, valor, label_atual])

            except ValueError:
                # Caso ocorra ruído na serial que não seja conversível em número, simplesmente ignora
                pass

    # "Loop recursivo" do Tkinter: Agenda esta mesma função para ser executada novamente após 5 ms
    janela.after(5, atualizar)


# CRIAÇÃO DOS BOTÕES E EXECUÇÃO

# Cria os botões e os vincula às suas respectivas funções através do parâmetro "command"
ttk.Button(janela, text="Gravar", command=iniciar_gravacao).grid(row=1, column=0, sticky="sw", padx=20, pady=20)
ttk.Button(janela, text="Salvar", command=salvar_dados).grid(row=1, column=1, sticky="s", padx=20, pady=20)
ttk.Button(janela, text="Label", command=criar_janelatk).grid(row=1, column=2, sticky="se", padx=20, pady=20)

# Inicia o ciclo infinito de leitura de dados chamando a função a primeira vez
atualizar()

# Inicia o loop principal de eventos do Tkinter (mantém a janela aberta e responsiva)
janela.mainloop()

# Código de Limpeza: Só chega nesta linha se a janela for fechada pelo usuário
if ser is not None:
    # Fecha a porta serial de forma segura para não deixar o recurso travado no sistema operacional
    ser.close()