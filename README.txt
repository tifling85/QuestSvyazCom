������� �����������

���� ����������������: Python3.6
�������: Ubuntu 18.04

������:

CalcServer.py
��������� ����� �� ���� 50000, ������� ����������� �� TCP. ������� �����������, ������� �������������� �����, ������ � ����� ����������� ������������ � ����� ������. �������� ����� ������� ����� ����������.
��� ������������� ����� ����������� ������� 30 ������. ���� �� ��� ����� ������ �� ����������������� - ����� �����������.
� ����� ������ ������� ������ �� �������. ��������� ������:
login ��� - �������� ����������������� �������. ��������� ������ � ���� MySql
calc ��������� - ��������� ��������� �� ������������, �����������.
���������� ������������ � �������������� �������� �������� ������ 
https://ru.wikipedia.org/wiki/%D0%9E%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D0%B0%D1%8F_%D0%BF%D0%BE%D0%BB%D1%8C%D1%81%D0%BA%D0%B0%D1%8F_%D0%B7%D0%B0%D0%BF%D0%B8%D1%81%D1%8C
��������� ������������� �������, ��� ������ � ������� ������������ ���������� ��� ���������� �������������� �������.
logout - �������������
� ������ ��������� ������������ ������ �������� ������� ��������� "incorrect command!"
� ���� ����� ������ ���������� ������� �� ������ CalcFunc.py

CalcFunc.py:
����� ��������� �������.
getConnection() - ������� ����������� � MySql ����
check_login(login) - ������� ������ � ��, ��������� ������������� �����
check_pass(login, password) - ������� ������ � ��, ��������� ������������ ������ ���������� �����
check_balance(login) - ������� ������ � ��, ���������� ������ �������� ������������
reduce_balance(login) - ������� ������ � ��, ��������� ������ ���������� ������������ �� 1
try_auth(login, conn) - ��������� ������� check_login � check_pass �������� ������� �������������� ������������. � ������ ����� ���������� ������� ������ ����������.
try_logout(login, conn, address) - ������������� ������������. ��������� ������� ������ ����������.
check_calc(data, login, conn) - ����������� ��� ������� 'calc ���������' ������������ ������������. ��������� ������������ ���������, ��������� ������, � ������ ������ �������� ��������� ������� sort_facility(data, conn).
sort_facility(data, conn) - "������������� �������", �������� ��� �������������� ��������� �� ��������� ������� � �������� �������� ������(�������). ������� ���������� ���� ���, ������� ���������� ������� rpn_on_stack(data, login, conn)
rpn_on_stack(data, login, conn) - ���������� ��������� ���. ��������� ��������� ���������, �������� ������� reduce_balance(login).
write_to_log(login, request, result) - ���������� ��������� ������� calc � ���� CalcLogs.txt.

CalcClient.py
������ ��� ������ � �������������. ������������ � �������(����� - ���������).

CalcTester.py:
������ ��� ��������� ��������. ������ ������ ��������� 'calc 1+1' ��� � �������.

CalcUnitTest.py:
��������� ��� ����������. �������� ������� �� ������, ��������� ����������, ���������, ��������� ��.

createDB.sh:
������ �� bash. ������������ � MySQL ����, ������� ������� � ��������.

CalcLogs.txt
����, ���� ������������ ���� ��� ���������� ������� calc

README.txt
������� ���� � ��������� �������.


������ ������ � ��������:
root@alexandr-H55M-S2H:/home/alexandr/python/TestSvyazcom# python3.6 CalcClient.py
Connecting to server..
Input command: calc 1+1
incorrect command!
Input command: login Apex
Invalid login!
Input command: login Alex
login correct. input password:
Input command: Mobilon
authentication failed!
Input command: login Alex
login correct. input password:
Input command: Mobilon123
authentication success!
Input command: calc 1+1
Result is: 2.0
Input command: calca 1+1
incorrect command!
Input command: calc 1/0
Result is: DivizionByZero!!!
Input command: calc 1+2*3
Result is: 7.0
Input command: logout
Alexlogout
Input command: calc 1+1
incorrect command!
Input command: login Vit
login correct. input password:
Input command: qwerty
authentication success!
Input command: calc 1-(1-5)
Result is: 5.0
Input command: logout
Vitlogout


������ � Calclogs:
15-09-2019 17:51        Alex    1+1     2.0
15-09-2019 17:52        Alex    1+2*3   7.0
15-09-2019 17:59        Vit     1-(1-5) 5.0
