
from CalcFunc import *

myHost = ''
myPort = 50000
#authstatus = {'Empty' : 'off', 'Alex': 'off'}
login = 'Empty'

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.bind((myHost, myPort))
sockobj.listen(5)

def handleClient(conn, login):
    print('Current user', login)
    mutex = thread.allocate_lock()
    if login == 'Empty':
        print('Timeout on!')
        conn.settimeout(30)
        
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            print('Recieve: ', data)
            if re.findall('login .+', data):
                login = try_auth(data.split(' ')[1], conn)
            elif re.findall('logout', data):
                login = try_logout(login, conn, address)
            elif re.findall('calc .+', data) and login != 'Empty':
                calc_list = check_calc(data[5:], login, conn)
                print('calc_list= ', calc_list)
                if not calc_list: continue
                stack_rpn = sort_facility(calc_list, conn)
                print('stack_rpn= ', stack_rpn)
                if not stack_rpn: continue
                result = rpn_on_stack(stack_rpn, login, conn)
                if not result: continue
                print('result = ', result)
                mutex.acquire()
                write_to_log(login, data[5:].replace(' ', ''), result)
                mutex.release()
            else:
                conn.send('incorrect command!'.encode('utf-8'))
        except timeout:
            print('socked close for timeout')
            break
        except BrokenPipeError:
            print('Socket by {} break!'.format(address))
            break
    conn.close()
    
while True:
    conn, address = sockobj.accept()
    print('Server connected by', address)
    thread.start_new_thread(handleClient, (conn, login))
    
