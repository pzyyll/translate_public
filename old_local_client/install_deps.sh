#!/usr/bin/env bash 

python -m pip install --upgrade pip
python -m pip install virtualenv --user
python -m venv .venv --clear

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

git submodule update --init --recursive
