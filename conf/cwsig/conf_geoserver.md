Install GeoServer:
====================


## 1 - Install GDAL: ##

```Bash
# be sure to have an updated system
sudo apt-get update && sudo apt-get upgrade -y

# install PROJ
sudo apt-get install libproj-dev proj-data proj-bin unzip -y

# install GEOS
sudo apt-get install libgeos-dev -y

# install GDAL
sudo apt-get install libgdal-dev python3-gdal gdal-bin -y

# install PDAL (optional)
sudo apt-get install libpdal-dev pdal -y


```



