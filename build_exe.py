import os
import subprocess
import shutil

# Очистка предыдущих сборок
def clean_previous_builds():
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Папка {folder} удалена.")

# Очищаем предыдущие сборки
clean_previous_builds()

# Название итогового .exe файла
exe_name = "SalaryManager.exe"

# Путь к главному скрипту
main_script = "main.py"

# Путь к иконке
icon_path = os.path.join("src", "assets", "logo.ico")

# Папки и файлы, которые нужно включить
data_files = [
    ("src\\data", "src\\data"), 
    ("src\\assets", "src\\assets"),  
]

# Формируем команду для PyInstaller
command = [
    "pyinstaller",
    "--noconfirm",  # Не запрашивать подтверждение
    "--onefile",  # Создать один .exe файл
    "--windowed",  # Без консоли (для GUI приложения)
    f"--name={exe_name}",  # Имя .exe файла
]

# Добавляем иконку, если она существует и корректна
if os.path.exists(icon_path):
    command.append(f"--icon={icon_path}")
else:
    print("Компилируем без иконки из-за проблем с logo.ico.")

# Добавляем пути к данным
for src, dst in data_files:
    command.append(f"--add-data={src}{os.pathsep}{dst}")

# Добавляем главный скрипт
command.append(main_script)

# Выполняем команду
try:
    print(f"Выполняем команду: {' '.join(command)}")  
    subprocess.run(command, check=True)
    print(f"Компиляция завершена! Файл {exe_name} создан в папке dist/")
except subprocess.CalledProcessError as e:
    print(f"Ошибка при компиляции: {e}")