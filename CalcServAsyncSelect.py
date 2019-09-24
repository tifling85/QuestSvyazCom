
from CalcFunc import *
import select
import time

myHost = ''
myPort = 50000
login = 'Empty'
SERVER_ADDRESS = ('localhost', 50000)
MAX_CONNECTIONS = 10
INPUTS = list()
OUTPUTS = list()
dict_sock = {}


def get_non_blocking_server_socket():

    server = socket(AF_INET, SOCK_STREAM)
    server.setblocking(0)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind(SERVER_ADDRESS)
    server.listen(MAX_CONNECTIONS)
    return server

    

def handle_readables(readable, server, dict_sock):
    for resource in readables:

        if resource is server:
            connection, client_address = resource.accept()
            connection.setblocking(0)
            INPUTS.append(connection)
            print("new connection from {address}".format(address=client_address))
            return (dict_sock)
            
        else:
            data = ""
            try:
                data = resource.recv(1024).decode('utf-8')
                print('Recieve: ', data)
                if re.findall('login .+', data):
                    if resource not in OUTPUTS:
                        OUTPUTS.append(resource)
                    print(dict_sock)
                    dict_sock[resource] = [data, 'login', data.split(' ')[1]]
                    return (dict_sock)
                if data == 'login':
                    if resource not in OUTPUTS:
                        OUTPUTS.append(resource)
                    dict_sock[resource][1] = 'show_login'
                    return (dict_sock)

                elif not data:
                    INPUTS.remove(resource)
                    if resource in OUTPUTS:
                        OUTPUTS.remove(resource)
                else:
                    if resource not in OUTPUTS:
                        OUTPUTS.append(resource)
                    dict_sock = {resource : [login, 'incorrect', '']}
                    print ('read', dict_sock)
                    return (dict_sock)

            except ConnectionResetError:
                #OUTPUTS.remove(resource)
                INPUTS.remove(resource)
                resource.close()
            except ConnectionAbortedError:
                #OUTPUTS.remove(resource)
                INPUTS.remove(resource)
                resource.close()

    return dict_sock
def handle_writables(writables):
    print('write', dict_sock)
    for resource in writables:
        print('write resource', resource)
        try:
            if dict_sock[resource][1] == 'incorrect':
                resource.send(bytes('incorrect command!', encoding='UTF-8'))
                OUTPUTS.remove(resource)
            if dict_sock[resource][1] == 'login':
                resource.send(bytes(dict_sock[resource][2], encoding='UTF-8'))
                OUTPUTS.remove(resource)
            if dict_sock[resource][1] == 'show_login':
                resource.send(bytes(dict_sock[resource][2], encoding='UTF-8'))
                OUTPUTS.remove(resource)
        except OSError:
            clear_resource(resource)

if __name__ == '__main__':
    server_socket = get_non_blocking_server_socket()
    INPUTS.append(server_socket)
    try:
        while INPUTS:
            #print('event loop 1', dict_sock)
            readables, writables, exceptional = select.select(INPUTS, OUTPUTS, INPUTS)
            print('read', readables)
            print ('write', writables)
            time.sleep(1)
            print('event loop 2', dict_sock)
            dict_sock = handle_readables(readables, server_socket, dict_sock)

                
            handle_writables(writables)
    except KeyboardInterrupt:        
        print("Server stopped! Thank you for using!")

    
