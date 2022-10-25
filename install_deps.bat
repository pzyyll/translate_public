cd /d %~dp0
python -m pip install --upgrade pip
python -m pip install virtualenv --user
python -m virtualenv .venv --clear

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

git submodule update --init --recursive