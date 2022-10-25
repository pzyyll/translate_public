cd /d %~dp0
call .venv/Scripts/activate.bat
pyinstaller.exe --clean .\translate.spec