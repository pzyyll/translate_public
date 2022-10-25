cd /d %~dp0
call .venv/Scripts/activate.bat
pyi-makespec --onefile --name translate translate.py
pyinstaller.exe --clean .\translate.spec