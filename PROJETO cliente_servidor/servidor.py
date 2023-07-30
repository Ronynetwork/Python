''' IMPORTANDO BIBLIOTECAS NECESSÁRIAS PARA O FUNCIONAMENTO DO CÓDIGO '''
from otherfunc import *
from Functions_and_Var import *

try:

    clients_list = {}
    while True:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((SERVER, PORT))
            PRINTS('Aguaradando conexão do cliente...')
            ServerLog.info(f'Servidor {SERVER} a espera de conexões na porta {PORT}!')
            server.listen()
            
            socket_client, client_info = server.accept()

            ServerLog.info (f'{client_info} Se conectou ao servidor.'); print('-'*100)
            clients_list[client_info[1]] = [client_info[0], socket_client] #Inserindo no dicionário a PORTA:IP do cliente
            tClient = threading.Thread(target=Client_Interaction, args=(socket_client, client_info, clients_list))

            tClient.start()
        except:
            ServerLog.critical(f'Erro na ao iniciar a Thread... {sys.exc_info()[0]}')
        
except OSError as e:
    ServerLog.critical ("Todas as portas do servidor estão ocupadas... ", e)

except SystemExit:
    print()

except:
    ServerLog.critical(f'Erro ao iniciar o Server... {sys.exc_info()[0]}')