#!/bin/bash

mysql -u root -pqwerty <<EOF
USE TestSvyaz;
CREATE table users1(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, login char(255), password char(255), balance int);
INSERT into users1(login, password, balance) VALUES ('Alex', 'Mobilon123', 100);
INSERT into users1(login, password, balance) VALUES ('Vit', 'qwerty', 1000);

