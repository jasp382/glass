GLASS | Setup development environment
================

## Clone glass repository

```Bash
sudo apt install git

git clone https://github.com/jasp382/glass ~/glass
```

## Install dependencies

* [Ubuntu 22.04](dep/ub22.md);

## Setup Python virtual environment

```Bash
# Create new virtual env
mkvirtualenv genv

workon genv

# Install GLASS
pip install --upgrade pip

cd ~/glass && pip install -r requirements.txt

pip install pygdal=="`gdal-config --version`.*"

OR 

ln -s /usr/lib/python3/dist-packages/osgeo* ~/.virtualenvs/genv/lib/python3.10/site-packages

pv=$(/usr/bin/python3 --version)
IFS=' '
read -a parr <<< "$pv"
pvv="${parr[1]}"

IFS='.'
read -a pvva <<< "$pvv"
pone="${pvva[0]}"
ptwo="${pvva[1]}"

echo "/home/$USER/glass" | sudo tee ~/.virtualenvs/genv/lib/python$pone.$ptwo/site-packages/glass.pth
```


### Set PGPASSFILE Environment variable:

```Bash
echo "export PGPASSFILE=/home/$USER/.pgpass" | sudo tee --append ~/.bashrc

sudo chmod 600 ~/.pgpass
source ~/.bashrc
```

### Replace osmconf file:

```Bash
sudo rm /usr/share/gdal/osmconf.ini

sudo cp ~/glass/conf/osmconf-gdal.ini /usr/share/gdal/osmconf.ini
```