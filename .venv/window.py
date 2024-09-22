import tkinter as tk
from tkinter import scrolledtext
from tarfile import TarFile, TarError
import argparse
import logging
import json

# Настройка логгера

class JsonFormatter(logging.Formatter):  # класс для внесения записи в лог-файл
    def __init__(self, username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
    def format(self, record):
        log_obj = {
            'time': self.formatTime(record, '%Y-%m-%d %H:%M:%S'),  # фиксация даты и времени
            'message': record.getMessage(),  # фиксация команды
            'username': self.username,  # фиксация имени пользователя
        }
        return log_obj

def initialize_log_file():
    with open(logfile_path, 'w', encoding='UTF-8') as f: # открытие лог-файла в режиме перезаписи
        json.dump([], f, ensure_ascii=False, indent=4)  # создание пустого json массива

def append_to_log(log_obj):
    try:
        with open(logfile_path, 'r', encoding='UTF-8') as f:
            log_data = json.load(f)  # чтение существующего содержимого лог-файла
    except (FileNotFoundError, json.JSONDecodeError):
        log_data = []  # если файл не существует или пустой, создание новый массив
    log_data.append(log_obj)  # добавление новой записи в массив
    with open(logfile_path, 'w', encoding='UTF-8') as f:  # запись обновленного json массива обратно в файл
        json.dump(log_data, f, ensure_ascii=False, indent=4)

# класс обработчика для записи в лог-файл
class CustomHandler(logging.Handler):
    def emit(self, record):
        log_obj = self.format(record) # форматирование записи к стандартному json формату
        append_to_log(log_obj) # добавление записи в лог-файл

# создание парсера для ввода параметров при запуске эмулятора из командной строки
parser = argparse.ArgumentParser(description='Эмулятор оболочки ОС')
# добавление получаемых аргументов
parser.add_argument('username', type=str, help='Имя пользователя')
parser.add_argument('hostname', type=str, help='Имя компльютера')
parser.add_argument('tarfile_path', type=str, help='Путь к файловой системе')
parser.add_argument('logfile_path', type=str, help='Путь к лог-файлу')

# установка данных для вывода в привественном сообщении
args = parser.parse_args()
username = args.username # получение имени пользователя
hostname = args.hostname # получение имени компьютера
tarfile_path = args.tarfile_path # получение пути к архиву
logfile_path = args.logfile_path # получение пути к лог-файлу

handler = CustomHandler() # объект - обработчик для записи в лог-файл
handler.setFormatter(JsonFormatter(username))
logger = logging.getLogger('command_logger') # создание логгера
# задание уровня логгирования, INFO - уровень для записи сообщений, сообщающих о нормальной работе
logger.setLevel(logging.INFO)
logger.addHandler(handler)

current_directory = '' # задание текущей директории

# Функция для обработки команд
def execute_command(event):
    global current_directory # добавление названия текущей директории в область видимости функции

    command = command_entry.get() # получение команды
    logger.info(command) # логгирование команды

    # добавление введенной команды в текстовое поле
    output_text.configure(state='normal')
    output_text.insert(tk.END, f"{command}\n")
    output_text.configure(state='disabled')

    try:
        with TarFile(tarfile_path, 'r') as files:
            if command == 'ls': # обработка команды ls
                if current_directory == '': # вывод файлов из верхеней директории (файловой системы)
                    output = "\n".join(member.name for member in files.getmembers() if member.name.find('/') == -1)
                else: # вывод файлов из установленной директории
                    output = "\n".join(member.name[len(current_directory) + 1:] for member in files.getmembers() if member.name.startswith(current_directory + '/'))
            elif command == "whoami": # обработка команды whoami
                output = username
            elif command.startswith('cd'): # обработка команды cd
                path = command.split()[1]
                if path == '..':  # переход на уровень вверх
                    if current_directory: # если текущая директория непустая
                        current_directory = '/'.join(current_directory.split('/')[:-1])
                        if not current_directory:
                            current_directory = ''
                        output = '' # выводимого сообщения нет
                else:  # переход в нужную директорию
                    new_directory = current_directory + '/' + path if current_directory else path
                    # проверка существования новой директории
                    if any(member.name.startswith(new_directory + '/') for member in files.getmembers()):
                        current_directory = new_directory
                        output = ''
                    else:
                        output = f"Ошибка: каталог '{path}' не найден."
            elif command.startswith('tail'): # обработка команды tail
                parts = command.split() # разделение введённой команды на части
                filename = parts[1] if len(parts) > 1 else None
                # задание количества строк для вывода, по умолчанию - 10
                lines_to_show = int(parts[2]) if (len(parts) > 2) else 10
                if filename:
                    try:
                        full_path = f"{current_directory}/{filename}" if current_directory else filename
                        content = files.extractfile(full_path).read().decode()
                        lines = content.splitlines()
                        last_lines = lines[-lines_to_show:]  # получение последних строк
                        output = "\n".join(last_lines)
                    except KeyError:
                        output = f"Ошибка: файл '{filename}' не найден в архиве."
                    except Exception as e:
                        output = f"Ошибка при чтении файла: {e}"
                else:
                    output = "Ошибка: необходимо указать имя файла."
            elif command == "exit": # обработка команды exit
                window.quit()
                return
            elif command == "history": # обработка команды history
                try:
                    # открытие лог-файла для чтения
                    with open(logfile_path, 'r', encoding='UTF-8') as log:
                        data = json.load(log) # чтение данных из лог-файла
                        output = ''
                        for i in data:
                            output += str(i) + "\n"
                except FileNotFoundError:
                    output = f"Ошибка: Файл {logfile_path} не найден."
                except json.JSONDecodeError as e:
                    output = f"Ошибка декодирования JSON: {e}. Проверьте корректность формата JSON в файле."
                except Exception as e:
                    output = f"Произошла ошибка: {e}."
            else:
                output = "Unknown command"

            # вывод результата в текстовое поле
            output_text.configure(state='normal')
            if output != '':
                output_text.insert(tk.END, f"{output}\n")
            output_text.configure(state='disabled')
    except Exception as e:
        output_text.configure(state='normal')
        output_text.insert(tk.END, f"Error: {str(e)}\n")
        output_text.configure(state='disabled')

    # очистка поля ввода
    command_entry.delete(0, tk.END)

    # обновление текста с приглашением ко вводу
    update_prompt()


# функция для обновления приглашения к вводу
def update_prompt():
    global username, hostname
    username = username # получение имени пользователя
    hostname = hostname # получение имени компьютера
    prompt = f"{username}@{hostname} $ " # составление текста приглашения

    output_text.configure(state='normal')
    output_text.insert(tk.END, prompt)  # добавляем приглашения
    output_text.see(tk.END)  # прокручтка вниз
    output_text.configure(state='disabled')


# создание основного окна
window = tk.Tk()
window.title("Shell Emulator")

# создание текстового поля для вывода
output_text = scrolledtext.ScrolledText(window, width=100, height=30, state='disabled')
output_text.pack(pady=10)

# изначальное приглашение ко вводу
update_prompt()

# создание поля ввода для команд
command_entry = tk.Entry(window, width=100)
command_entry.pack(pady=10)
command_entry.bind('<Return>', execute_command)  # Привязка клавиши Enter к функции

# установка курсора в поле ввода при запуске
command_entry.focus()

# создание пустого лой-файла
initialize_log_file()

# запуск основного цикла GUI
window.mainloop()