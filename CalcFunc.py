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
            query = 'SELECT * from users where login = \'{}\''.format(login)
            cursor.execute(query)
            for row in cursor:
                return True
            return False

def check_pass(login, password):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = 'SELECT password from users where login = \'{}\''.format(login)
            cursor.execute(query)
            for row in cursor:
                if row['password'] == password : return True
                else: return False

def check_balance(login):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = 'SELECT balance from users where login = \'{}\''.format(login)
            cursor.execute(query)
            for row in cursor:
                return row['balance']
            
def reduce_balance(login):
    with closing (getConnection()) as connection:
        with connection.cursor() as cursor:
            query = 'UPDATE users set balance = balance - 1 where login = \'{}\''.format(login)
            cursor.execute(query)
            connection.commit()
            return
        
def try_auth(login, conn):
    if check_login(login):
        conn.send('login correct. input password:'.encode('utf-8'))
        data = conn.recv(1024).decode('utf-8')
        if check_pass(login, data):
            conn.send('authentication success!'.encode('utf-8'))
            #authstatus[login] = 'on'
            conn.settimeout(None)
            print('user ' + login + ' is logged')
            print('Timeout off!')
            print(check_balance(login))
            return login
        else:
            conn.send('authentication failed!'.encode('utf-8'))
            return 'Empty'
    else:
        conn.send('Invalid login!'.encode('utf-8'))
        return 'Empty'
        
def try_logout(login, conn, address):
    if login == 'Empty': 
        conn.send('You are not logging!'.encode('utf-8'))
        return 'Empty'
    print(address, login, 'logout')
    conn.send((login + 'logout').encode('utf-8'))
    #authstatus[login] = 'off'
    conn.settimeout(30)
    print('Timeout on!')
    return 'Empty'

def check_calc(data, login, conn):
    print(data)
    #if not re.findall(r'^[\d+\+*/()-]+$', data):
    if check_balance(login) == 0:
        conn.send('Balance is NULL!'.encode('utf-8'))
        return False
    data = data.replace(' ', '')
    print(data)
    if not re.fullmatch('(?:[()]*[0-9]+[.,]?[0-9]*[()]*[\+*/()-]?[()]*)+', data):
        conn.send('Incorrect data!'.encode('utf-8'))
        return False
    #return re.findall('(\d+|[\+*/()-])', data)
    return re.findall('([0-9]+[.,]?[0-9]*|[\+*/()-])', data)

def sort_facility(data, conn):
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
        conn.send('Inconsistent brackets!'.encode('utf-8'))
        return False
    else:
        return outstr

def rpn_on_stack(data, login, conn):
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
    conn.send('Result is: {0}'.format(stack[-1]).encode('utf-8'))
    reduce_balance(login)
    print(check_balance(login))
    return stack.pop()

def write_to_log(login, request, result):
    time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    with open ('CalcLogs.txt', 'a') as f:
        f.write(time + '\t' + login + '\t' + request + '\t' + str(result) + '\n')
    return
