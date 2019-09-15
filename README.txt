Сетевой калькулятор

Язык программирования: Python3.6
Система: Ubuntu 18.04

Модули:

CalcServer.py
открывает сокет на порт 50000, ожидает подключение по TCP. Получив подключение, создает дополнительный поток, работа с новым соединением продолжается в новом потоке. Основной поток ожидает новых соединений.
Для подключенного сокет запускается таймаут 30 секунд. Если за это время клиент не аутентифицируется - сокет закрывается.
В новом потоке ожидает данных от клиента. Возможные данные:
login имя - пытается аутентифицировать клиента. создается запрос в базу MySql
calc выражение - проверяет выражение на корректность, высчитывает.
вычисления производятся с использованием Обратной польской записи 
https://ru.wikipedia.org/wiki/%D0%9E%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D0%B0%D1%8F_%D0%BF%D0%BE%D0%BB%D1%8C%D1%81%D0%BA%D0%B0%D1%8F_%D0%B7%D0%B0%D0%BF%D0%B8%D1%81%D1%8C
результат записываетсяв логфайл, при работе с которым используется блокиратор для исключения одновременного доступа.
logout - разлогинивает
В случае получение некорректных данных отсылает клиенту сообщение "incorrect command!"
В ходе своей работы использует функции из модуля CalcFunc.py

CalcFunc.py:
Здесь находятся функции.
getConnection() - создает подключение к MySql базе
check_login(login) - создает запрос в БД, проверяет существование имени
check_pass(login, password) - создает запрос в БД, проверяет соответствие пароля указанному имени
check_balance(login) - создает запрос в БД, возвращает баланс текущего пользователя
reduce_balance(login) - создает запрос в БД, уменьшает баланс указанного пользователя на 1
try_auth(login, conn) - используя функции check_login и check_pass проводит процесс аутентификации пользователя. В случае удачи сбрасывает таймаут сокета соединения.
try_logout(login, conn, address) - разлогинивает пользователя. запускает таймаут сокета соединения.
check_calc(data, login, conn) - запускается при команде 'calc выражение' залогиненого пользователя. проверяет корректность выражения, проверяет баланс, в случае успеха передает выражение функции sort_facility(data, conn).
sort_facility(data, conn) - "сортировочная станция", алгоритм для преобразования выражения из инфиксной нотации в обратную польскую запись(нотацию). Функция возвращает стек ОПЗ, который передается функции rpn_on_stack(data, login, conn)
rpn_on_stack(data, login, conn) - реализация алгоритма ОПЗ. Вычисляет результат выражения, вызывает функцию reduce_balance(login).
write_to_log(login, request, result) - записывает результат команды calc в файл CalcLogs.txt.

CalcClient.py
Клиент для работы с калькулятором. подключается к серверу(адрес - локалхост).

CalcTester.py:
Клиент для генерации нагрузки. Спамит сервер запросами 'calc 1+1' раз в секунду.

CalcUnitTest.py:
Программа для юниттестов. Посылает команды на сервер, принимает результаты, проверяет, совпадают ли.

createDB.sh:
скрипт на bash. подключается к MySQL базе, создает таблицу с записями.

CalcLogs.txt
Файл, куда записываются логи при выполнении команды calc

README.txt
Текущий файл с описанием проекта.


Пример работы с клиентом:
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


записи в Calclogs:
15-09-2019 17:51        Alex    1+1     2.0
15-09-2019 17:52        Alex    1+2*3   7.0
15-09-2019 17:59        Vit     1-(1-5) 5.0
