from CalcFuncAsyncIODB import *

mutex = thread.allocate_lock()

async def handleClient(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connecting from {addr!r}")
    login = 'Empty'
    print('Current user', login)
    if login == 'Empty':
        print('Timeout on!')
        task = asyncio.create_task(conn_timeout(writer))
    while True:
        message = ((await reader.readline()).decode('utf-8')).rstrip()
        if writer.is_closing(): break
        print('Recieve from {}: {}'.format(login, message))
        if re.findall('login .+', message):
            login = await try_auth(message.split(' ')[1:], reader, writer)
            if login != 'Empty':
                task.cancel()
        elif re.findall('logout', message):
            login, task = await try_logout(login, reader, writer)
        elif re.findall('calc .+', message) and login != 'Empty':
            calc_list = await check_calc(message[5:], login, reader, writer)
            #print('calc_list= ', calc_list)
            if not calc_list: continue
            stack_rpn = await sort_facility(calc_list, reader, writer)
            #print('stack_rpn= ', stack_rpn)
            if not stack_rpn: continue
            result = round(await rpn_on_stack(stack_rpn, login, reader, writer), 2)
            if not result and result != 0: continue
            print('result = ', result)
            mutex.acquire()
            write_to_log(login, message[5:].replace(' ', ''), result)
            mutex.release()
        else:
            writer.write('incorrect command!'.encode('utf-8'))

async def main():
    server = await asyncio.start_server(handleClient, '127.0.0.1', 50000)
    addr = server.sockets[0].getsockname()
    print(addr)
    async with server:
        await server.serve_forever()



asyncio.run(main())    
