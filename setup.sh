#! /bin/bash

# install python3
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew update && brew upgrade

brew install python3

python3 setup.py install

python3 -m pip install grpcio

python3 -m pip install grpcio-tools

