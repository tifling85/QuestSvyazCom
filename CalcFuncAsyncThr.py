from contextlib import closing
from socket import *
import re
import operator
import pymysql
from pymysql.cursors import DictCursor
from contextlib import closing
import os.path
import datetime
import _thread as thread
import asyncio
import logging
import threading

def getConnection():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='qwerty',                             
                                 db='TestSvyaz',
                                 charset='utf8mb4',
                                 cursorclass=DictCursor)
    return connection



def check_login(login):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = "SELECT id from users1 where login=%s"
            cursor.execute(query, (login,))
            for row in cursor:
                return True
            return False

def check_pass(login, password):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = "SELECT `password` from `users1` where `login`=%s"
            cursor.execute(query, (login,))
            for row in cursor:
                if row['password'] == password : return True
                else: return False

def check_balance(login):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = "SELECT `balance` from `users1` where `login`=%s"
            cursor.execute(query, (login,))
            for row in cursor:
                return row['balance']
            
def reduce_balance(login):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = "UPDATE `users1` SET `balance` = `balance` - 1  where `login`=%s"
            cursor.execute(query, (login,))
            connection.commit()
            return
        
async def try_auth(login, client, loop):
    print(login)
    if check_login(login):
        await loop.sock_sendall(client, 'login correct. input password:'.encode('utf8'))
        data = (await loop.sock_recv(client, 1024)).decode('utf-8')
        if check_pass(login, data):
            await loop.sock_sendall(client, 'authentification success!!'.encode('utf8'))
            print('user ' + login + ' is logged')
            print('Timeout off!')
            print(check_balance(login))
            return login
        else:
            await loop.sock_sendall(client, 'authentication failed!'.encode('utf8'))
            return 'Empty'
    else:
        await loop.sock_sendall(client, 'Invalid login!'.encode('utf8'))
        return 'Empty'
        
async def try_logout(login, client, addr, loop):
    if login == 'Empty':
        await loop.sock_sendall(client, 'You are not logging!'.encode('utf8'))
        return ('Empty', '') 
    print(login, ' logout')
    await loop.sock_sendall(client, (login + ' logout').encode('utf8'))
    task = asyncio.create_task(conn_timeout(client, addr))
    print('Timeout on!')
    return ('Empty', task)

async def check_calc(data, login, client, loop):
    print(data)
    if check_balance(login) == 0:
        await loop.sock_sendall(client, 'Balance is NULL!'.encode('utf8'))
        return False
    data = data.replace(' ', '')
    print(data)
    if not re.fullmatch('(?:[()]*[0-9]+[.,]?[0-9]*[()]*[\+*/()-]?[()]*)+', data):
        await loop.sock_sendall(client, 'Incorrect data!'.encode('utf8'))
        return False
    return re.findall('([0-9]+[.,]?[0-9]*|[\+*/()-])', data)

async def sort_facility(data, client, loop):
    stack, outstr = [], []
    rates = {'+': 1, '-': 1, '*': 2, '/': 2, '(':0}
    operators = ['+', '-', '/', '*', '(']
    for token in data:
        if token in operators:
            if stack and token != '(':
                while stack:
                    if rates[token] <= rates[stack[-1]]:
                        outstr.append(stack.pop())
                    else:
                        stack.append(token)
                        break
                else: stack.append(token)
            else: stack.append(token)
        elif token is ')':
            while stack[-1] != '(':
                outstr.append(stack.pop())
            stack.pop()
        else:
            outstr.append(float(token))
        print(outstr)
        print(stack)

    for token in stack[::-1]:
        outstr.append(token)
    if '(' in stack:
        print('Inconsistent brackets!')
        await loop.sock_sendall(client, 'Inconsistent brackets!'.encode('utf8'))
        return False
    else:
        return outstr

async def rpn_on_stack(data, login, client, loop):
    operators = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv}
    stack = [0]
    for token in data:
        print(token)
        if token in operators:
            oprnd2, oprnd1 = stack.pop(), stack.pop()
            print('token is {}, oprnd2 is {}'.format(token, oprnd2))
            if token == '/' and oprnd2 == 0.0:
                conn.send('Result is: DivizionByZero!!!'.encode('utf-8'))
                return False
            stack.append(operators[token](oprnd1,oprnd2))
            print(stack)
        elif token or token == 0.0:
            stack.append(float(token))
            print(stack)
    await loop.sock_sendall(client, 'Result is: {0}'.format(stack[-1]).encode('utf8'))
    reduce_balance(login)
    print(check_balance(login))
    return stack.pop()

def write_to_log(login, request, result):
    time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    with open ('CalcLogs.txt', 'a') as f:
        f.write(time + '\t' + login + '\t' + request + '\t' + str(result) + '\n')
    return

async def conn_timeout(client, addr, handle_task):
    log = logging.getLogger()
    log.info('Timeout for %s, %i on!' % (addr[0], addr[1]))
    #print(client)
    await asyncio.sleep(10)
    log.info('Timeout for %s, %i !' % (addr[0], addr[1]))
#    try:
#        #handle_task.cancel()
#        client.close()
#    except OSError:
#        print('OSError')
    print('aaaaaaaaa ne rabotaet...')
    #time.sleep(5)