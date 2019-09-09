from socket import *
import re
myHost = ''
myPort = 50000

authlist = {'Alex': 'Mobilon123'}
authstatus = {'Empty' : 'off', 'Alex': 'off'}
login = 'Empty'

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.bind((myHost, myPort))
sockobj.listen(5)

def try_auth(login):
    print(login)
    if authlist.get(login):
        conn.send('login correct. input password:'.encode('utf-8'))
        data = conn.recv(1024).decode('utf-8')
        if data == authlist['Alex']:
            conn.send('authentication success!'.encode('utf-8'))
            authstatus[login] = 'on'
            return login
        else:
            conn.send('authentication failed!'.encode('utf-8'))
            return 'Empty'
    else:
        conn.send('Invalid login!'.encode('utf-8'))
        return 'Empty'
        
def try_logout(login):
    print(login, authstatus[login])
    if login == 'Empty' or authstatus[login] == 'off': 
        conn.send('You are not logging!'.encode('utf-8'))
        return 'Empty'
    print(address, login, 'disconnected')
    conn.send((login + 'logout').encode('utf-8'))
    authstatus[login] = 'off'
    return 'Empty'

while True:
    conn, address = sockobj.accept()
    print('Server connected by', address)
    while True:
        data = conn.recv(1024).decode('utf-8') # читать следующую строку из сокета
        print(data)
        if re.findall('login', data):
            login = try_auth(data.split(' ')[1])
        elif re.findall('logout', data):
            login = try_logout(login)
        else:
            conn.send('incorrect input!'.encode('utf-8'))
    
    conn.close()
    