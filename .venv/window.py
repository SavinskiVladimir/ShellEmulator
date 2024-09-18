import tkinter as tk
from tkinter import scrolledtext
from tarfile import TarFile, TarError
import os
import logging
import json

# Настройка логгера
logfile_path = 'log.json'  # путь к лог-файлу

class JsonFormatter(logging.Formatter):  # класс для внесения записи в лог-файл
    def format(self, record):
        log_obj = {
            'time': self.formatTime(record, '%Y-%m-%d %H:%M:%S'),  # фиксация даты и времени
            'message': record.getMessage(),  # фиксация команды
            'username': os.getlogin(),  # фиксация имени пользователя
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

# создание обработчика для записи в файл
class CustomHandler(logging.Handler):
    def emit(self, record):
        log_obj = self.format(record)
        append_to_log(log_obj)

handler = CustomHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger('command_logger')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

current_directory = 'D:/дз/конф_управление/shellemulator/.venv/files.tar'

# Функция для обработки команд
def execute_command(event):
    command = command_entry.get()
    logger.info(command)

    # Добавляем введенную команду в текстовое поле
    output_text.configure(state='normal')
    output_text.insert(tk.END, f"{command}\n")  # Выводим команду
    output_text.configure(state='disabled')

    try:
        with TarFile('files.tar', 'r') as files:
            if command == 'ls':
                output = "\n".join(member.name for member in files.getmembers())
            elif command == "whoami":
                output = os.getlogin()
            elif command.startswith('cd'):
                path = command.split()[1]
                if path == '..':  # переход на уровень вверх
                    if current_directory:
                        current_directory = '/'.join(current_directory.split('/')[:-1])
                else:  # Переход в указанный каталог
                    new_directory = current_directory + '/' + path if current_directory else path
                    # Проверка существования нового каталога в архиве
                    if any(member.name.startswith(new_directory + '/') for member in files.getmembers()):
                        current_directory = new_directory
                    else:
                        output = f"Ошибка: каталог '{path}' не найден."
            elif command.startswith('tail'):
                parts = command.split()
                filename = parts[1] if len(parts) > 1 else None
                lines_to_show = int(parts[2]) if (len(parts) > 2) else 10  # Значение по умолчанию
                if filename:
                    try:
                        content = files.extractfile(filename).read().decode()
                        lines = content.splitlines()
                        last_lines = lines[-lines_to_show:]  # Получаем последние строки
                        output = "\n".join(last_lines)
                    except KeyError:
                        output = f"Ошибка: файл '{filename}' не найден в архиве."
                    except Exception as e:
                        output = f"Ошибка при чтении файла: {e}"
                else:
                    output = "Ошибка: необходимо указать имя файла."
            elif command == "exit":
                window.quit()
                return
            elif command == "history":
                try:
                    with open(logfile_path, 'r', encoding='UTF-8') as log:
                        data = json.load(log)
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

            # Вывод результата в текстовое поле
            output_text.configure(state='normal')
            output_text.insert(tk.END, f"{output}\n")
            output_text.configure(state='disabled')
    except Exception as e:
        output_text.configure(state='normal')
        output_text.insert(tk.END, f"Error: {str(e)}\n")
        output_text.configure(state='disabled')

    # Очистка поля ввода
    command_entry.delete(0, tk.END)

    # Обновление текста с приглашением
    update_prompt()


# Функция для обновления приглашения к вводу
def update_prompt():
    username = os.getlogin()
    hostname = os.environ['COMPUTERNAME']
    tarfile_path = 'files.tar'
    prompt = f"{username}@{hostname} : {tarfile_path} (log: {logfile_path}) $ "

    output_text.configure(state='normal')
    output_text.insert(tk.END, prompt)  # Добавляем новое приглашение
    output_text.see(tk.END)  # Прокручиваем вниз
    output_text.configure(state='disabled')


# Создание основного окна
window = tk.Tk()
window.title("Tar Emulator")

# Создание текстового поля для вывода
output_text = scrolledtext.ScrolledText(window, width=80, height=20, state='disabled')
output_text.pack(pady=10)

# Изначальное приглашение к вводу
update_prompt()

# Создание поля ввода для команд
command_entry = tk.Entry(window, width=80)
command_entry.pack(pady=10)
command_entry.bind('<Return>', execute_command)  # Привязка клавиши Enter к функции

# Установка курсора в поле ввода при запуске
command_entry.focus()

initialize_log_file()

# Запуск основного цикла GUI
window.mainloop()