import threading, socket
from Functions_and_Var import *


try:
    server = conn_server()
    clients = {}
    while True:
        sock_client, end = server.accept()
        PRINTS(f'Conexão TCP estabelecida.\n\nCliente {end[0]} conectado na porta {end[1]}.')
        clients[end[0]] = end[1]
        tClient = threading.Thread(target=Client_Interaction, args=(sock_client,end,clients))
        tClient.start()
        except:
            print()
except OSError as e:
    if e.errno == 98:
        print('Todas as portas do servidor estão ocupadas')
    else:
        print('Erro ao estabelecer a conexão do servidor:', e)