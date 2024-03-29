from var import *
from otherfunc import *
from functions_download import *
from run import *
#-------------------------------------------------------------------------------------------------------------------------------------------------

#                                                          PARTE CLIENTE                                                                     #

def user_interaction(sock):
    msg = b''
    while msg != '/q':
        try:
            msg = input(PROMPT)
            if msg[0] == '/u':
                msg_split = msg.split(':')
                size = os.path.getsize(msg_split[1])
                comunicacao = msg + f':{str(size)}'
                sock.send(comunicacao.encode(CODE))
                
            if msg != '': sock.send(msg.encode(CODE))
        except:
            msg = '/q'
            exit()


def server_interaction(sock):
    try:
        msg = b''
        while True:
            msg = sock.recv(512)
            if not msg:  # Se a mensagem estiver vazia, significa que o servidor encerrou a conexão.
                break
            recebimento = msg.decode(CODE)
            print(recebimento)
    except Exception as exceção:
        print(f'Erro na comunicação com o servidor: {exceção}')
    finally:
        PRINTS('Você solicitou o fim da conexão.\nAté a próxima!!')
        sock.close()
        exit()

#                                                        PARTE DO SERVIDOR                                                                  #
# -----------------------------------------------------------------------------------------------------------------------------------------------

def conn_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((SERVER, PORT))
        PRINTS(f'\nServidor {SERVER} a espera de conexões na porta {PORT}!\n')
        server.listen()
        
        return server
    except:
        ServerLog.eror(f'Erro ao estabelecer a conexão do servidor{sys.exc_info()[0]}')
        server.close()
  

# -----------------------------------------------------------------------------------------------------------------------------------------------

#                                                    FUNÇÕES INTERATIVAS DO SERVIDOR                                                        #

def broadCast(clients_list, client_info, comunicacao):
    comunicacao_div = SPLIT(comunicacao)
    msg = f'O cliente: {client_info[0]} | {client_info[1]} Enviou uma mensagem para todos!\nMensagem > {comunicacao_div[1]}'
    try:
        for key, value in clients_list.items():
            if key != client_info[1]:
                sock_broadcast = value[1]
                sock_broadcast.send(msg.encode(CODE))
        ServerLog.info('Foi solicitado o comando /f -> Listagem dos arquivos do servidor.')
        ServerLog.info(f'A mensagem enviada via broadcast foi {comunicacao_div[1]}')
    except:
        ServerLog.error(f'Erro ao enviar mensagem em Broadcast... {sys.exc_info()[0]}')
        exit()

# -----------------------------------------------------------------------------------------------------------------------------------------------

#                             FUNÇÃO QUE PRINTA TODOS OS COMANDOS E MENSAGENS TROCADAS ENTRE O CLIENTE E O SERVIDOR       #               

def HISTORY(historic, socket_client):
    try:
        
        msg = f'\nEsse é seu histórico de comandos:\n\n'
        qtd = 0
        for x in historic:
            qtd +=1
            msg += f'{qtd} {x}\n'
        socket_client.send(msg.encode(CODE))
        ServerLog.info('Foi solicitado o comando /h -> Historico de mensagens.')

    except:
        ServerLog.error(f'Erro no envio do History... {sys.exc_info()[0]}')
# -------------------------------------------------------------------------------------------------------------------------------------------------

#                                           FUNÇÃO QUE LISTA TODOS OS CLIENTES CONECTADOS NO SERVIDOR                                         #

def List_Clients(clients_list, socket_client):
    try: 
        title = "\nOs Clientes conectados ao Servidor são:" # formatando mensagem 
        socket_client.send(title.encode(CODE)) 
        num = 0
        for chave, valor in clients_list.items():  # faço um for para pegar cada cliente conectado e enviar  
            num+=1 # formatação numeração cliente
            comunicacao_list = f"\nCLIENTE {num}\nIP: {valor[0]}\nPORT: {chave}\n" # formatação listagem clientes (lembrando que chave=porta e valor[0]=ip)
            socket_client.send(comunicacao_list.encode(CODE)) # enviando mensagens 
        ServerLog.info('Foi solicitado o comando /l -> Listagem dos clientes conectados no servidor.')
    except:
        ServerLog.error(f'Erro no momento de Listar os Clientes Conectados...{sys.exc_info()[0]}')  
        exit()

# -------------------------------------------------------------------------------------------------------------------------------------------------

#                                      FUNÇÃO QUE EXPLICA A FUNCIONALIDADE DE TODAS AS OUTRAS FUNÇÕES                                         #
def HELP(socket_client):
    try:
        # Criando descrição de cada comando
        options = {
        '/l': 'Listar os clientes conectados',
        '/m:ip:porta:mensagem': 'Enviar mensagem para um cliente especifíco (informe IP:PORTA do cliente) depois digite sua mensagem',
        '/b:mensagem': 'Enviar mensagem para todos clientes conectados',
        '/h': 'Lista o seu histórico de comandos',
        '/?': 'Lista as opções disponiveis',
        '/q': 'Desconectar do Servidor',
        '/d:nome_do_arquivo': 'Enviar arquivo do servidor para o cliente',
        '/w:url': 'Efetuar o download de um arquivo a partir da url informada',
        '/u:nome_arquivo': 'Enviar um arquivo para o servidor\n'
        }
        title = f"\nSegue abaixo as Opções disponiveis neste servidor:"
        socket_client.send(title.encode(CODE))
        for com, describ in options.items(): # listando por meio do FOR comando por comando 
            help_com = f"\n{com} -> {describ}" # formatação mensagem
            socket_client.send(help_com.encode(CODE)) # enviando comando por comando
            ServerLog.info('Foi solicitado o comando /? -> Listagem dos comandos do servidor.')

    except:
        ServerLog.error(f'Erro ao listar as Opções...{sys.exc_info()[0]}')  
        exit()  
# -------------------------------------------------------------------------------------------------------------------------------------------------

#                                   função que envia uma mensagem do cliente para outro em específico                                         #

def Private(socket_client, comunicacao, clients_list):
        comunicacao = SPLIT(comunicacao)
        for key, value in clients_list.items():
            try:
                if str(key) == comunicacao[2] and value[0] == comunicacao[1]:
                    PRINTS('Enviando a mensagem para o cliente informado...\nAguarde.')
                    sock_destination = value[1]
                    sock_destination.send((f'O cliente: {clients_list[0]}:{clients_list[1]} enviou uma mensagem para você.').encode(CODE))
                    ServerLog.info('Foi solicitado o comando /m -> mensagem privada.')
                    ServerLog.info((f'O cliente: {clients_list[0]}:{clients_list[1]} recebeu uma mensagem -> {comunicacao[3]}'))
            except:
                socket_client.send((f'Não foi possível localizar o cliente informado... {sys.exc_info()[0]}').encode(CODE))

# -------------------------------------------------------------------------------------------------------------------------------------------------
'''                                             FUNÇÃO QUE LISTA OS ARQUIVOS PRESENTES EM SERVER_FILES                                          '''
def List_Server(socket_client):
    try:
        local =  os.path.dirname(os.path.abspath(__file__)) + '\\server_files\\'
        # Obtém a lista de itens (arquivos e diretórios) no diretório especificado
        itens_no_diretorio = os.listdir(local)
        socket_client.send(f'Estes são os arquivos presentes na pasta do servidor e seus respectivos tamanhos:\n'.encode(CODE))
        # Filtra apenas os arquivos
        for item in itens_no_diretorio:
            lenght = os.path.getsize(local+item)
            socket_client.send(f'({item}): {lenght} bytes;\n'.encode(CODE))
        socket_client.send('\nCaso deseje realizar o download de algum arquivo, por favor utilizar o comando (/d:(nome do arquivo)).'.encode(CODE))
        ServerLog.info('Foi solicitado o comando /f -> Listagem dos arquivos do servidor.')
    except FileNotFoundError:
        ServerLog.debug("Diretório não encontrado.")


#-------------------------------------------------------------------------------------------------------------------------------------------------

#                                       INTERAÇÃO ENTRE AS MENSAGENS RECEBIDAS E OS COMANDOS ENVIADOS                                        #

def Client_Interaction(socket_client, client_info, clients_list):
    try:
        historic = []
        while True:
            comunicacao = socket_client.recv(512).decode(CODE).lower()
            command = SPLIT(comunicacao)
            if command[0] == '/?':
                HELP(socket_client)
            elif command[0].strip() == '/q':
                ServerLog.critical(f'O cliente: ({client_info[0]}, {client_info[1]}) solicitou o fim da conexão.')
                del clients_list[client_info[1]]
                socket_client.close()
                break
            elif command[0] == '/b':
                broadCast(clients_list, client_info, comunicacao)
            elif command[0] == '/f':
                List_Server(socket_client)
            elif command[0] == '/h':
                HISTORY(historic, socket_client)
            elif command[0] == '/l':
                List_Clients(clients_list, socket_client)
            elif command[0] == '/m':
                Private(socket_client, comunicacao, clients_list)
            elif command[0] == '/w':
                DOWNLOAD(socket_client, comunicacao)

            else:
                ServerLog.info(f'O cliente(IP/PORTA): ({client_info[0]}, {client_info[1]}) -> enviou uma mensagem: {command[0]}')
            historic.append(command[0])
    except SystemExit:
        ServerLog.debug('Foi acionada a função exit')


