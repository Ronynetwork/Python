import os, sys, socket, ssl
local = os.path.dirname(os.path.abspath(__file__)) 
print(local)
sys.path.append(local + '\\Funções')
import funções_link, funções_download

# Utilizando de função para modelar a url
link_quebrado, url_host, url_image, n_img, arq_txt, protocolo = funções_link.link_change()

'''print('-'*100)
print(arq_txt)
print(f'Host: {url_host}\nLocal_imagem: {url_image}')
print(f'Nome_imagem: {n_img}\nExtensão: {extensão}\nProtocolo: {protocolo}')
print('-'*100)'''

# Realizando a conexão
if protocolo == 'http':
    socket_img = funções_download.connect_http(url_host, url_image)
    print('Conexão estabelecida!'); print('-'*100)

elif protocolo == 'https':
    socket_img = funções_download.connect_https(url_host, url_image)
    print('Conexão estabelecida!'); print('-'*100)

else:
    print('Protocolo não suportado... Tente novamente com HTTP ou HTTPS\n')
    exit()

buffer_size = 4096
# Pegando e armazenando o retorno dos dados
retorno = b''
while True:
    data = socket_img.recv(buffer_size)
    if not data: 
        break
    retorno += data
#Fechando a conexão
socket_img.close()

delimiter = '\r\n\r\n'.encode()
position  = retorno.find(delimiter) #Pegando a posição de início do cabeçalho
headers   = retorno[:position] # Armazenando o cabeçalho em Headers
image     = retorno[position+4:] # Pegando apenas a imagem

print('-'*100,'\n')
print(str(headers, 'utf-8'),'\n')
print('-'*100)

# Definindo o local do head
nome_cabeçalho = f'\\cabeçalho.' + arq_txt
local_cabeçalho = local + f'\\{nome_cabeçalho}'
# salvando o head em um arquivo
try:
    with open(local_cabeçalho, 'w', encoding='utf-8') as header:
        header.write(headers.decode('utf-8'))
except:
    print(f'Erro na criação do arquivo txt...{sys.exc_info()[0]}')

headers = headers.decode('utf-8')
try:
    linhas = headers.strip().split('\n') # pego o header já decodificado e quebro ele em linhas
    for x in linhas:
        if x.startswith('Content-Type') or x.startswith('content-type'): # Busco nessas linhas o content-type por meio do startswich que retorna True quando a palavra existir
            extensão = x.strip().split('/')[1] # pego a linha do Content-type, retiro os espaços com strip() e quebro com split() onde tiver uma barra
            break # com isso para o for, pois já tenho a extensão
    html_verification = extensão.find(';') # EXCEÇÃO: quando a url é de um arquivo HTML, temos que fazer um filtro diferente para conseguir pegar a extensão
    if html_verification != -1:
        extensão = extensão.split(';')[0] # usamos split() para quebrar a extensão onde tiver ';' e pego o primeiro resultado 
        # formato content type HTML -> html; charset = utf-8

except:
    print(f'\nErro na captura do Content-Type...{sys.exc_info()[0]}\n')
print(extensão)
# Salvando a imagem
nome_final = f'{n_img}.' + extensão # Definindo o nome da imagem
imagem = local + f'\\{nome_final}' # Definindo o local de download

try:
    with open(imagem, 'wb') as arquivo:
        arquivo.write(image)
except:
    print(f'Erro ao salvar a imagem...{sys.exc_info()[0]}')
    exit()