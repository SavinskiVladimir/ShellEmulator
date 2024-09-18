from tarfile import TarFile, TarError
import os
import logging
import json

def is_non_empty_tar_file(tarfile_path):
  try:
    with TarFile.open(tarfile_path, 'r') as tar:
      return len(tar.getmembers()) > 0
  except (TarError, FileNotFoundError):
    return False

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


username = os.getlogin()  # получение имени пользователя
hostname = os.environ['COMPUTERNAME']  # получение имени компьютера
tarfile_path = 'files.tar'  # получение пути к архиву

current_directory = 'D:/дз/конф_управление/shellemulator/.venv/files.tar'

initialize_log_file() # создание пустого лог-файла

with TarFile('files.tar', 'r') as files:
  while True:

    prompt = f"{username}@{hostname} : {tarfile_path} (log: {logfile_path}) $ "
    command = input(prompt) # ввод команды
    logger.info(command) # логгирование команды

    if command == 'ls':
      for member in files.getmembers():
         print(member.name)
    elif command == "exit":
      break
    elif command.startswith('cd'):
        path = command.split()[1]
        if path == '..': # переход на уровень вверх
            if current_directory:
                current_directory = '/'.join(current_directory.split('/')[:-1])
        else: # Переход в указанный каталог
            new_directory = current_directory + '/' + path if current_directory else path
            # Проверка существования нового каталога в архиве
            if any(member.name.startswith(new_directory + '/') for member in files.getmembers()):
                current_directory = new_directory
            else:
                print(f"Ошибка: каталог '{path}' не найден.")
    elif command == "whoami":
        print(username)
    elif command.startswith('tail'):
        parts = command.split()
        filename = parts[1] if len(parts) > 1 else None
        lines_to_show = int(parts[2]) if (len(parts) > 2) else 10 # Значение по умолчанию
        if filename:
            try:
                content = files.extractfile(filename).read().decode()
                lines = content.splitlines()
                last_lines = lines[-lines_to_show:]  # Получаем последние строки
                print("\n".join(last_lines))
            except KeyError:
                print(f"Ошибка: файл '{filename}' не найден в архиве.")
            except Exception as e:
                print(f"Ошибка при чтении файла: {e}")
        else:
            print("Ошибка: необходимо указать имя файла.")
    elif command == "history":
        try:
            with open(logfile_path, 'r', encoding='UTF-8') as log:
                data = json.load(log)
                for i in data:
                    print(i)
        except FileNotFoundError:
            print(f"Ошибка: Файл {logfile_path} не найден.")
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}. Проверьте корректность формата JSON в файле.")
        except Exception as e:
            print(f"Произошла ошибка: {e}.")
