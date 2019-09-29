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
import aiomysql


async def getConnection():
    connection = await aiomysql.connect(host='localhost',
                                 user='root',
                                 password='qwerty',                             
                                 db='TestSvyaz')
    return connection

async def check_login(login):  
    with closing (await getConnection()) as connection:
        async with connection.cursor() as cursor:
            print("SELECT `id` FROM `users1` WHERE `login`='{}'".format(login))
            await cursor.execute("SELECT `id` FROM `users1` WHERE `login`=%s", (login,))
            r = await cursor.fetchall()
            if not r: return False
#            print(r)
            if r[0][0]: return True
            return False

async def check_pass(login, password):
    with closing (await getConnection()) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `password` from `users1` where `login`=%s", (login,))
            r = await cursor.fetchone()
#            print(r[0])
            if r[0] == password: return True
            return False

async def check_balance(login):
    with closing (await getConnection()) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT `balance` from `users1` where `login`=%s", (login,))
            r = await cursor.fetchone()
#            print(r[0])
            return r[0]
            
async def reduce_balance(login):
    with closing (await getConnection()) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE `users1` SET `balance` = `balance` - 1  where `login`=%s", (login,))
            await connection.commit()
            return
        
async def try_auth(login, reader, writer):
    login = ' '.join(login)
    if await check_login(login):
        writer.write('login correct. input password:'.encode('utf-8'))
        await writer.drain()
        data = ((await reader.readline()).decode('utf-8')).rstrip()
        if await check_pass(login, data):
            writer.write('authentication success!'.encode('utf-8'))
            await writer.drain()
            print('user ' + login + ' is logged')
            print('Timeout off!')
            print(await check_balance(login))
            return login
        else:
            writer.write('authentication failed!'.encode('utf-8'))
            await writer.drain()
            return 'Empty'
    else:
        writer.write('Invalid login!'.encode('utf-8'))
        await writer.drain()
        return 'Empty'
        
async def try_logout(login, reader, writer):
    if login == 'Empty':
        writer.write('You are not logging!'.encode('utf-8'))
        await writer.drain()
        return ('Empty', '') 
    print(login, ' logout')
    writer.write((login + ' logout').encode('utf-8'))
    await writer.drain()
    task = asyncio.create_task(conn_timeout(writer))
    print('Timeout on!')
    return ('Empty', task)

async def check_calc(data, login, reader, writer):
#    print(data)
    if await check_balance(login) < 1:
        writer.write('Balance is NULL!'.encode('utf-8'))
        await writer.drain()
        return False
    data = data.replace(' ', '')
    print(data)
    if not re.fullmatch('(?:[()]*[0-9]+[.,]?[0-9]*[()]*[\+*/()-]?[()]*)+', data):
        writer.write('Incorrect data!'.encode('utf-8'))
        await writer.drain()
        return False
    return re.findall('([0-9]+[.,]?[0-9]*|[\+*/()-])', data)

async def sort_facility(data, reader, writer):
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
#        print(outstr)
#        print(stack)

    for token in stack[::-1]:
        outstr.append(token)
    if '(' in stack:
        print('Inconsistent brackets!')
        writer.write('Inconsistent brackets!'.encode('utf-8'))
        return False
    else:
        return outstr

async def rpn_on_stack(data, login, reader, writer):
    operators = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv}
    stack = [0]
    for token in data:
#        print(token)
        if token in operators:
            oprnd2, oprnd1 = stack.pop(), stack.pop()
            print('token is {}, oprnd2 is {}'.format(token, oprnd2))
            if token == '/' and oprnd2 == 0.0:
                conn.send('Result is: DivizionByZero!!!'.encode('utf-8'))
                return False
            stack.append(operators[token](oprnd1,oprnd2))
#            print(stack)
        elif token or token == 0.0:
            stack.append(float(token))
#            print(stack)
    writer.write('Result is: {0}'.format(stack[-1]).encode('utf-8'))
    await writer.drain()
    await reduce_balance(login)
    print(await check_balance(login))
    return stack.pop()

def write_to_log(login, request, result):
    time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    with open ('CalcLogs.txt', 'a') as f:
        f.write(time + '\t' + login + '\t' + request + '\t' + str(result) + '\n')
    return

async def conn_timeout(writer):
    await asyncio.sleep(20)
    print('timeout!')
    writer.close()
