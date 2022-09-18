#! /bin/bash
STRING="Null Byte"
echo "Hackers love to learn on $STRING"

# install python3
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew update && brew upgrade

brew install python3

python3 setup.py install

