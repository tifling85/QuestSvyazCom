import asyncio, socket, time,threading
import concurrent.futures
import logging,sys
from CalcFuncAsyncThr import *
mutex = thread.allocate_lock()
mutex_accept = thread.allocate_lock()
HOST=''
PORT=50000
server = socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server.bind((HOST,PORT))
server.listen(8)
server.setblocking(False)

async def handle_client(client, addr, loop):
    log = logging.getLogger()
    log.info('connecting from %s, %i' % (addr[0], addr[1]))
    login = 'Empty'
    log.info('Current user %s' % (login))    
#    Таймаут сломался
#    if login == 'Empty':
#        try:
#            task = asyncio.create_task(conn_timeout(client, addr, handle_task))
#        except OSError:
#            print('OSError')
#        #print(asyncio.all_tasks())
    while True:
        try:
            message = (await loop.sock_recv(client, 1024)).decode('utf-8')
            if message == '': break
            log.info('Recieve from %s : %s' %(login, message))
            if re.findall('login .+', message):
                login = await try_auth(message.split(' ')[1], client, loop)
                if login != 'Empty':
                    task.cancel()
            elif re.findall('logout', message):
                login, task = await try_logout(login, client, addr, loop)
            elif re.findall('calc .+', message) and login != 'Empty':
                calc_list = await check_calc(message[5:], login, client, loop)
                #print('calc_list= ', calc_list)
                if not calc_list: continue
                stack_rpn = await sort_facility(calc_list, client, loop)
                #print('stack_rpn= ', stack_rpn)
                if not stack_rpn: continue
                result = round(await rpn_on_stack(stack_rpn, login, client, loop), 2)
                if not result and result != 0: continue
                print('result = ', result)
                mutex.acquire()
                write_to_log(login, message[5:].replace(' ', ''), result)
                mutex.release()
            else:
                await loop.sock_sendall(client, 'Incorrect command!'.encode('utf8'))
        except (ConnectionAbortedError, timeout):
            log.info('Client disconnect')
            break
    client.close()
    log.info('closing')

async def run_server(loop):
    log = logging.getLogger()
    while True:
        log.info('running')
        # Попытка сделать очередность у потоков
#        while mutex_accept.locked():
#            #log.info('zalo4eno')
#            await asyncio.sleep(0)
#        mutex_accept.acquire()
#        log.info('set block')
        client, addr = await loop.sock_accept(server)
#        mutex_accept.release()
#        time.sleep(0.1)
#        log.info('unset block')
        
        asyncio.create_task(handle_client(client, addr, loop))


def rserver():
    while True:
        print('start loop')
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_server(loop))

async def create_threads(executor):    
    accepts = [loop.run_in_executor(executor, rserver,) for i in range(2)]
    completed, pending = await asyncio.wait(accepts)

logging.basicConfig(
        level=logging.INFO,
        format='%(threadName)10s %(name)18s: %(message)s',
        stream=sys.stderr)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=2,)
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(create_threads(executor))
finally:
    loop.close()