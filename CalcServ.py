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
    if authlist.get(login):
        conn.send('login correct. input password:'.encode('utf-8'))
        data = conn.recv(1024).decode('utf-8')
        if data == authlist['Alex']:
            conn.send('authentication success!'.encode('utf-8'))
            authstatus[login] = 'on'
            conn.settimeout(None)
            print('user ' + login + ' is logged')
            print('Timeout off!')
            return login
        else:
            conn.send('authentication failed!'.encode('utf-8'))
            return 'Empty'
    else:
        conn.send('Invalid login!'.encode('utf-8'))
        return 'Empty'
        
def try_logout(login):
    if login == 'Empty' or authstatus[login] == 'off': 
        conn.send('You are not logging!'.encode('utf-8'))
        return 'Empty'
    print(address, login, 'logout')
    conn.send((login + 'logout').encode('utf-8'))
    authstatus[login] = 'off'
    conn.settimeout(30)
    print('Timeout on!')
    return 'Empty'

while True:
    conn, address = sockobj.accept()
    print('Server connected by', address)
    print('Current user', login)
    if login == 'Empty':
        print('Timeout on!')
        conn.settimeout(30)
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            print('Recieve: ', data)
            if re.findall('login .+', data):
                login = try_auth(data.split(' ')[1])
            elif re.findall('logout', data):
                login = try_logout(login)
            else:
                conn.send('incorrect input!'.encode('utf-8'))
        except timeout:
            print('socked close for timeout')
            break
    
    conn.close()
    
