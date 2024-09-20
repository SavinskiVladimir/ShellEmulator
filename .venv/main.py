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

# установка данных для вывода в привественном сообщении
username = os.getlogin()  # получение имени пользователя
hostname = os.environ['COMPUTERNAME']  # получение имени компьютера
tarfile_path = 'files.tar'  # получение пути к архиву

current_directory = '' # установка текущей директории (вначале - сама файловая система является директорией)

initialize_log_file() # создание пустого лог-файла

with TarFile('files.tar', 'r') as files:
  while True:

    prompt = f"{username}@{hostname} : {tarfile_path} (log: {logfile_path}) $ "
    command = input(prompt) # ввод команды
    logger.info(command) # логгирование команды

    if command == 'ls':
      for member in files.getmembers():
        if current_directory == '': # вывод содержимого самого верхнего каталога
            if (member.name.find('/') == -1):
                print(member.name)
        elif member.name.startswith(current_directory + '/'): # вывод содержимого уставноленной директории
            print(member.name[len(current_directory) + 1:])
    elif command == "exit":
      break
    elif command.startswith('cd'):
        path = command.split()[1]
        if path == '..':  # переход на уровень вверх
            if current_directory:
                current_directory = '/'.join(current_directory.split('/')[:-1])
                if not current_directory:  # если поднялись на уровень выше и текущий каталог пустой, устанавливаем его в корень
                    current_directory = ''
        else:  # переход в указанный каталог
            new_directory = current_directory + '/' + path if current_directory else path
            # проверка существования нового каталога в архиве
            if any(member.name.startswith(new_directory + '/') for member in files.getmembers()):
                current_directory = new_directory
            else:
                print(f"Ошибка: каталог '{path}' не найден.")
    elif command == "whoami":
        print(username)
    elif command.startswith('tail'):
        parts = command.split()
        filename = parts[1] if len(parts) > 1 else None
        lines_to_show = int(parts[2]) if (len(parts) > 2) else 10 # количество строк для вывода, по умолчанию - 10
        if filename:
            try:
                full_path = f"{current_directory}/{filename}" if current_directory else filename
                content = files.extractfile(full_path).read().decode() # получение содержимого файла
                lines = content.splitlines() # разделение полученного содержимого на строки
                last_lines = lines[-lines_to_show:]  # получение последние строки
                print("\n".join(last_lines)) # сбор сообщения для вывода
            except KeyError:
                print(f"Ошибка: файл '{filename}' не найден в архиве.")
            except Exception as e:
                print(f"Ошибка при чтении файла: {e}")
        else:
            print("Ошибка: необходимо указать имя файла.")
    elif command == "history":
        try:
            with open(logfile_path, 'r', encoding='UTF-8') as log: # открытие лог-файла для чтения
                data = json.load(log) # чтение данных из лог-файла
                for i in data:
                    print(i)
        except FileNotFoundError:
            print(f"Ошибка: Файл {logfile_path} не найден.")
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}. Проверьте корректность формата JSON в файле.")
        except Exception as e:
            print(f"Произошла ошибка: {e}.")
