import sys
from cx_Freeze import setup, Executable
from cx_Freeze.initscripts import Console

# Замените 'your_script.py' на имя вашего скрипта PyQt5
script_name = 'SetupApp.py'

# Создание экземпляра Executable
executables = [Executable(script_name, base=None)]

# Настройки cx_Freeze
build_options = {
    'build_exe': {
        'includes': [
            'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
            'os', 'requests', 'subprocess', 'shutil', 'threading'
        ],
        'include_files': [

            ('icon/tab.ico', 'icon/tab.ico'),  # Директория с вашей иконкой
        ],
    },
}

# Настройки setup
setup(
    name="SetupApp",
    version="1.0",
    description="Описание вашей программы",
    options={
        'build_exe': build_options,
    },
    executables=executables,
    # Включить создание консольного скрипта
    cmdclass={"build_exe": Console},
)