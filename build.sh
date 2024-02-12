#!/bin/bash

echo $(dirname "$0")

cd $(dirname "$0")

source .venv/bin/activate

if [ ! -f ./translate.spec ] ; then 
    pyi-makespec --onefile --name translate translate.py
fi

pyinstaller --clean ./translate.spec