Install GLASS Dependencies in Ubuntu 14.04 LTS
====================

## 1 - Install Python and Pip:

```
sudo apt update
sudo apt install software-properties-common
sudo apt install python3 python3-pip
sudo -H pip3 install --upgrade pip
```

## 2 - Install GDAL and GRASS GIS:

```
sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
sudo apt update && sudo apt upgrade
sudo apt install grass grass-dev
```

**Set GDALDATA environment variable:**

```
echo "export GDAL_DATA=/usr/share/gdal" | sudo tee --append ~/.bashrc
echo "export PROJ_LIB=/usr/share/proj" | sudo tee --append ~/.bashrc
source ~/.bashrc
```
