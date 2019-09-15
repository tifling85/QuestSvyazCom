from socket import *
import re
import time

serverHost = 'localhost'
serverPort = 50000
unitlist = {
            'calc 1/0':'DivizionByZero!!!',
            'calc 1+1':'2.0',
            'calc 1 - 5+2.5':'-1.5',
            'calc -5*3+15':'0.0',
            'calc 1+2*5':'11.0',
            'calc 1-3-(5-10)':'3.0',
            'calc 2*(11-(5-3))/6': '3.0',
            'calc 4/(3-3)': 'DivizionByZero!!!'
            }

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((serverHost, serverPort))
print('Connecting to server..')
login = 'login Alex'
sockobj.send(login.encode('utf-8'))
#time.sleep(1)
data = sockobj.recv(1024).decode('utf-8')
sockobj.send('Mobilon123'.encode('utf-8'))
data = sockobj.recv(1024).decode('utf-8')
print(data)
for unit in unitlist:
    print(unit)
    sockobj.send(unit.encode('utf-8'))
    data = sockobj.recv(1024).decode('utf-8')
    print(data)
    if data == 'Result is: {}'.format(unitlist[unit]): print('Ok')
    else: print('Failed!!!')
sockobj.close()
