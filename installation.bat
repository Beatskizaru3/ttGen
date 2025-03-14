@echo off
REM --- Скрипт для установки Python 3.10.16 и необходимых библиотек ---

REM Указываем URL установщика Python 3.10.16 (64-бит)
set PYTHON_URL=https://www.python.org/ftp/python/3.10.16/python-3.10.16-amd64.exe
set INSTALLER=python-3.10.16-amd64.exe

echo [1/3] Скачивание установщика Python 3.10.16...
REM Используем PowerShell для скачивания файла
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER%'"

echo [2/3] Установка Python 3.10.16 в тихом режиме...
REM Устанавливаем Python для всех пользователей и добавляем его в PATH
%INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

REM Немного подождем, чтобы установка завершилась
timeout /t 10 >nul

echo Проверка установленной версии Python:
python --version

echo [3/3] Установка необходимых pip библиотек...
pip install certifi==2025.1.31
pip install charset_normalizer==3.4.1
pip install colorama==0.4.6
pip install decorator==5.2.1
pip install idna==3.10
pip install imageio==2.37.0
pip install imageio-ffmpeg==0.6.0
pip install moviepy==2.1.2
pip install numpy==2.2.3
pip install pillow==10.4.0
pip install proglog==0.1.10
pip install python_dotenv==1.0.1
pip install requests==2.32.3
pip install setuptools==65.5.0
pip install tqdm==4.67.1
pip install urllib3==2.3.0

echo.
echo Установка завершена!
pause

