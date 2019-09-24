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
            query = 'SELECT * from users1 where login = \'{}\''.format(login)
            cursor.execute(query)
            for row in cursor:
                return True
            return False

def check_pass(login, password):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = 'SELECT password from users1 where login = \'{}\''.format(login)
            cursor.execute(query)
            for row in cursor:
                if row['password'] == password : return True
                else: return False

def check_balance(login):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = 'SELECT balance from users1 where login = \'{}\''.format(login)
            cursor.execute(query)
            for row in cursor:
                return row['balance']
            
def reduce_balance(login):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = 'UPDATE users1 set balance = balance - 1 where login = \'{}\''.format(login)
            cursor.execute(query)
            connection.commit()
            return
        
async def try_auth(login, reader, writer):
    if check_login(login):
        writer.write('login correct. input password:'.encode('utf-8'))
        await writer.drain()
        
        #data = (await reader.read(1024)).decode('utf-8')
        #len_message = int((await reader.read(1024)).decode('utf-8'))
        data = ((await reader.readline()).decode('utf-8')).rstrip()
        if check_pass(login, data):
            writer.write('authentication success!'.encode('utf-8'))
            await writer.drain()
            print('user ' + login + ' is logged')
            print('Timeout off!')
            print(check_balance(login))
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
    print(data)
    #if not re.findall(r'^[\d+\+*/()-]+$', data):
    if check_balance(login) == 0:
        writer.write('Balance is NULL!'.encode('utf-8'))
        await writer.drain()
        return False
    data = data.replace(' ', '')
    print(data)
    if not re.fullmatch('(?:[()]*[0-9]+[.,]?[0-9]*[()]*[\+*/()-]?[()]*)+', data):
        writer.write('Incorrect data!'.encode('utf-8'))
        await writer.drain()
        return False
    #return re.findall('(\d+|[\+*/()-])', data)
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
        print(outstr)
        print(stack)

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
    writer.write('Result is: {0}'.format(stack[-1]).encode('utf-8'))
    await writer.drain()
    reduce_balance(login)
    print(check_balance(login))
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
