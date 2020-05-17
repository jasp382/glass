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
mkvirtualenv glassenv --system-site-packages
workon glassenv

# Install GLASS
pip install --upgrade pip
pip install yolk3k

cd ~/glass/core && pip install -r requirements.txt
pgdal=$(yolk -V pygdal)
pip install "${pgdal// /$'=='}"

pv=$(/usr/bin/python3 --version)
pvv="${pv:7:3}"
echo "/home/$USER/glass/core" | sudo tee ~/.virtualenvs/glassenv/lib/python$pvv/site-packages/glass.pth
```
