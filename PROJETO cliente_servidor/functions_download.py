import socket, ssl
from otherfunc import *
from var import *
#                                                                     VARIÁVEIS                                                                   <:


def PRINTS(x):
    print('-'*100)
    print(x)
    print('-'*100)

# ---------------------------------------------------------------------------------------------------------------------------------------------------
def sock_https(local_arq, host):
    req = f'GET {local_arq} HTTP/1.1\r\nHOST: {host}\r\nConnection: close\r\n\r\n'    # define a requisição 
    try:
        context = ssl.create_default_context()      # criação do contexto SSL para conexão HTTPS
        context.check_hostname = False      # desativa a verificação do nome do host durante a autenticação SSL.
        context.verify_mode = ssl.CERT_NONE     # o certificado do servidor não será verificado
        socket_TCP_IPV4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # criação do socket/ conexão com o server (IPV4/TCP)
        socket_conexão = context.wrap_socket(socket_TCP_IPV4, server_hostname=host)     # Envolve o socket criado anteriormente em uma conexão segura (wrap_socket)
    except:
        print(f'Erro na conexão HTTPS com a url informada... {sys.exc_info()[0]}')
        
    socket_conexão.connect((host, 443))     # estabelece a conexão
    socket_conexão.send(req.encode(CODE))     # enviando requisição pedida acima
    return socket_conexão # retornando conexão 


# ---------------------------------------------------------------------------------------------------------------------------------------------------

def sock_http(local_arq, host):
    requisição = f'GET {local_arq} HTTP/1.1\r\nHOST: {host}\r\nConnection: close\r\n\r\n'

    try:
        socket_conexão = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print(f'Erro na conexão HTTP com a url informada... {sys.exc_info()[0]}')

    socket_conexão.connect((host, 80))
    socket_conexão.sendall(requisição.encode(CODE))
    return socket_conexão

def CONT_LENGHT(header):
    try:
        lines = header.strip().split('\n')
        for line in lines:
            if line.lower().startswith('content-lenght:'): # vasculho nessas linhas o content-type por meio do startswich que retorna True quando a palavra existir
                tam = line.strip().split(':')[1]
                return tam
    except:
        print(f'Erro ao localizar o content-type... {sys.exc_info()[0]}')

# --------------------------------------------------------------------------------------------------------------------------------------------------

def CONT_TYPE(header):
    try:
        lines = header.strip().split('\n')
        for line in lines:
            if line.lower().startswith('content-type:'): # vasculho nessas linhas o content-type por meio do startswich que retorna True quando a palavra existir
                extension = line.strip().split('/')[1]
                return extension
    except:
        print(f'Erro ao localizar o content-type... {sys.exc_info()[0]}')

# ----------------------------------------------------------------------------------------------------------------------------------------------------

def DOWNLOAD_WEB(socket_conexão, sock_client):
    data_ret = b'' 
    dados_recebidos = 0
    try:
        content_lenght = -1
        msg_download = f'\nDownload do Arquivo foi Iniciado!\n'
        
        sock_client.send(msg_download.encode(CODE))

        while True:     # recebendo a resposta 
            data = socket_conexão.recv(BUFFER)    # recebe a resposta em pedaços de Xbytes (x = buffer_size)
            if not data: 
                break
            data_ret += data
            dados_recebidos += len(data)    # joga na variavel o quanto de bytes já foram recebidos
            position  = data_ret.find('\r\n\r\n'.encode(CODE))
            header   = data_ret[:position].decode('utf-8').lower()   # pegando o cabeçalho 
        if content_lenght == -1:
            msg_size = 'Não foi possivel capturar o Content_Lenght...'
            sock_client.send(msg_size.encode(CODE)) # criando um aviso para quando o content lenght não for pego 
        arquivo_dados = data_ret[position+4:]   # pegando os dados do arquivo
        content_type = CONT_TYPE(header) # usando a função para pegar a extensão do arquivo pelo header
        msg_download = f'\nO Download do arquivo foi concluído!\n'
        try:
            socket_conexão.send(msg_download.encode(CODE))
        except:
            print(f'\nErro ao enviar mensagem para o cliente...{sys.exc_info()[0]}')
    except:
        print(f'\nErro no recebimento dos dados...{sys.exc_info()}')  
        exit()  
    socket_conexão.close() # fechando a conexão
    return header, arquivo_dados, content_type

# -----------------------------------------------------------------------------------------------------------------------------------------
def DOWNLOAD(socket_client, comunicacao):
    try:
        url_brute = str(comunicacao[3:]) # pegando a URL do comando (/m:URL) apartir da 3° posição
        try:
            host, local_arq, name_arq, protocolo = SPLIT_URL(url_brute) # Realizando split da URL para pegar parametros especificos
        except:
            erro = '\nInforme a URL corretamente... (tente novamente)!\n' # Realizo tratamento fora da função [motivo: debug facilitado]
            MSG_CLIENT(socket_client, erro)
            return
        
        try:        
            # Realizando conexão HTTP/HTTPS a depender da URL
            if protocolo =='https': 
                socket_conexão = sock_https(local_arq, host)  
            elif protocolo =='http':
                socket_conexão = sock_http(local_arq, host)   
            else:
                erro = '\nProtocolo Não suportado... Em Desenvolvimento...\n' 
                MSG_CLIENT(socket_client, erro)
        except:
            erro = '\nA Requisição não teve sucesso, verifique a URL... (tente novamente)!\n'
            MSG_CLIENT(socket_client, erro)
            return
        
        # Separei as funções para a DOWNLOAD_WEB realizar o bruto [motivo: debug facilitado/redução de código/modulação]
        dados, content_type = DOWNLOAD_WEB(socket_conexão, socket_client) # me retorna o arquivo/extensão dele
        nome_arquivo = f'{name_arq}.{content_type}' # definindo o nome do arquivo com o nome retirado da URL + sua extensão real 
        diretorio_arquivo = dir + f'\\server_files\\{nome_arquivo}' # definindo local de save
        with open(diretorio_arquivo, 'wb') as arquivo: # gravando o arquivo
            arquivo.write(dados)
        ServerLog.info('Foi solicitado o comando /w -> Download por vida de uma url.')
    except IndexError: # caso do cliente não passar todos os argumentos necessários
        erro = "\nInforme todos os argumentos/parametros necessários para essa opção\n"
        MSG_CLIENT(socket_client, erro)

    except:
        ServerLog.error(f'Erro no momento de fazer o Download da URL...{sys.exc_info()[0]}')  
        exit()  
# ----------------------------------------------------------------------------------------------------------------------------
def UPLOAD(socket_client, comunicacao, dir_atual):
    try:
        local_arq = dir_atual + f'\\server_files\\{comunicacao[1]}'
        with open(local_arq, 'wb') as arquivo:
            msg_upload = f'\nGravando Arquivo no Servidor\nNome: {comunicacao[1]}\nTamanho: {comunicacao[2]} bytes\n'
            MSG_CLIENT(socket_client, msg_upload) # enviando mensagem para o cliente 
            bytes_recebidos = 0 
            pct = 1
            while True: 
                data_arquive = socket_client.recv(BUFFER) # Recebendo o conteúdo 
                if not data_arquive: break
                arquivo.write(data_arquive) # escrevendo 
                bytes_recebidos += len(data_arquive) # adicionando cada pacote de bytes aos bytes recebidos
                msg_upload = f'Pacote ({pct}) - Dados: {bytes_recebidos}/{comunicacao[2]} bytes\n' # informando o processamento
                MSG_CLIENT(socket_client, msg_upload)
                if bytes_recebidos >= comunicacao[2]: break # após os bytes recebidos forem iguais ou excederem o tamanho enviado antecipadamente, ele encerra.
                pct += 1
        msg_upload = f'\n\nO Upload do arquivo {comunicacao[1]} foi finalizado!\n' # informando que o Upload foi feito com sucesso
        
        ServerLog.info('Foi solicitado o comando /u -> Upload do arquivo para o servidor.')
        ServerLog.info(f'O upload do arquivo: {comunicacao[1]} foi finalizado.')
        MSG_CLIENT(socket_client, msg_upload)
    except FileNotFoundError: # erro já tratado no lado cliente, apenas para evitar logs 
        msg = f'O arquivo de nome {comunicacao[1]} não foi encontrado.'
        MSG_CLIENT(socket_client, msg)
    except:
        ServerLog.error(f'Erro no recebimento dos dados pelo Upload [Lado servidor]...{sys.exc_info()[0]}')

