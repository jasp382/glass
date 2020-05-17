GLASS | Setup development environment
================

## Clone glass repository

```
sudo apt install git

mkdir ~/code
git clone https://github.com/jasp382/glass ~/glass
```

## Install dependencies

* [Ubuntu 18.04](dep/ub18.md);

* [Ubuntu 20.04](dep/ub20.md);

* [MacOS](dep/macos.md);

## Setup Python virtual environment

```Bash
# Create new virtual env
mkvirtualenv glassenv
# OR
mkvirtualenv glassenv --system-site-packages

workon glassenv

# Install GLASS
pip install --upgrade pip

cd ~/glass/core && pip install -r requirements.txt

pip install pygdal=="`gdal-config --version`.*"

pv=$(/usr/bin/python3 --version)
IFS=' '
read -a parr <<< "$pv"
pvv="${parr[1]}"

IFS='.'
read -a pvva <<< "$pvv"
pone="${pvva[0]}"
ptwo="${pvva[1]}"

echo "/home/$USER/glass/core" | sudo tee ~/.virtualenvs/glassenv/lib/python$pone.$ptwo/site-packages/glass.pth
```
