from socket import *
import re
import time

serverHost = 'localhost'
serverPort = 50000

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((serverHost, serverPort))
print('Connecting to server..')
login = 'login Alex'
sockobj.send(login.encode('utf-8')) 
time.sleep(1)
data = sockobj.recv(1024).decode('utf-8')
sockobj.send('Mobilon123'.encode('utf-8'))
time.sleep(1)
while True:
    sockobj.send('calc 1+1'.encode('utf-8')) 
    time.sleep(1)
    data = sockobj.recv(1024).decode('utf-8')
    print(data)
    if re.findall('Goodbye', data): break


sockobj.close()