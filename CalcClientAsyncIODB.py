from socket import *
import re,sys,time

serverHost = 'localhost'
serverPort = 50000

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((serverHost, serverPort))
print('Connecting to server..')
while True:
    login = input('Input command: ') + '\n'
    
    if login == '': continue
    login = login.encode('utf-8')
    #len_log = str(len(login)) + '\n'
    #sockobj.send(len_log.encode())
    #time.sleep(1)
    sockobj.send(login) 
    data = sockobj.recv(1024).decode('utf-8')
    print(data)
    if re.findall('Goodbye', data): break


sockobj.close()