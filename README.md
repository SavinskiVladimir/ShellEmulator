# Домашняя работа №1 по предмету "Конфигурационное управление" студента группы ИКБО-40-23 Савинского Владимира Олеговича

## Постановка задачи
Требуется разработать эмулятор для языка оболочки ОС. Необходимо сделать работу 
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС. 
Эмулятор должен запускаться из реальной командной строки.
Эмулятор принимает образ виртуальной файловой системы в виде файла формата 
tar. Эмулятор должен работать в режиме GUI.

Ключами командной строки задаются:
- имя пользователя для показа в приглашении к вводу;
- имя компьютера для показа в приглашении к вводу;
- путь к архиву виртуальной файловой системы;
- путь к лог файлу.

Лог-файл имеет формат json и содержит все действия
во время последнего сеанса работы с эмулятором.
Для каждого действия фиксируются дата, время, имя пользователя.

Требуется поддержать команды ls, cd, exit, whoami, tail, history.

## Содержимое проекта

В проекте содержаться 3 файла расширения .py:
- main.py - отладочный файл, использовавшийся в процессе разработки для настройки корректной обработки команд, настройки логгера;
- window.py - основной файл, содержащий полноценный эмулятор с реализованным GUI интерфейсом. Интерфейс реализован средствами библиотеки Tkinter;
- window_file_input.py - файл, дублирующий содержимое файла window.py, но реализующий ввод команд из файла commands.txt, а также записывающий результаты работы эмулятор в файл output.txt.

## Пример работы эмулятора

![image](https://github.com/user-attachments/assets/0e0091d6-fdb3-437e-9c8c-a644e8254403)

На рисунке продемонстирована работа эмулятора.
Приглашение ко вводу имеет следующую структуру: user_name@computer_name $ command

## Тестирование

Протестируем обработку всех команд.
### ls и cd
Протестируем вывод содержимого всех директорий: корневой, dir1, dir2.
На рисунке продемонстрирован последовательный вывод содержимого директорий в порядке корень - dir1 - dir2.
![image](https://github.com/user-attachments/assets/6c6188e9-5544-4895-98c2-28e84dc6e7d7)
### whoami
Протестируем вывод имени текущего пользователя при помощи команды whoami.
![image](https://github.com/user-attachments/assets/36a1fcac-97da-4287-bf7c-ea678ac64b05)
### history
Для демонстрации работы history введём перед этим несколько команд.
![image](https://github.com/user-attachments/assets/3182285f-10c5-4e60-b5ae-5d6a7f12d607)
Запись о команде имеет следующую структуру: время ввода команды, текст команды, имя пользователя, который ввёл команду.
### tail
Продемонстрируем работу команды tail. По умолчанию количество выводимых строк равно 10.
![image](https://github.com/user-attachments/assets/287a6e02-7a9f-4986-bbbb-abb095b0292d)
### exit
При вводе команды exit происходит закрытие окна эмулятора.
