Install GLASS Dependencies in Ubuntu 14.04 LTS
====================

## 1 - Install Python and Pip:

```
sudo apt update
sudo apt install software-properties-common
sudo apt install python3 python3-pip
sudo -H pip3 install --upgrade pip
```

## 2 - Install PostgreSQL: ##

```
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list

sudo apt update

sudo apt -y install postgresql-10 postgresql-client-10
```

## 3 - Compile and install GDAL: ##

```
sudo apt install build-essential flex make bison gcc libgcc1 g++ cmake ccache python3-dev python3-opengl python-wxversion python-wxtools python3-dateutil python3-numpy wx3.0-headers wx-common libwxgtk3.0-dev libwxbase3.0-dev libncurses5-dev libbz2-dev zlib1g-dev gettext libtiff5-dev libpnglite-dev libcairo2 libcairo2-dev sqlite3 libsqlite3-dev libpq-dev libreadline6-dev libfreetype6-dev libfftw3-3 libfftw3-dev libboost-thread-dev libboost-program-options-dev liblas-c-dev subversion checkinstall libglu1-mesa-dev libxmu-dev ghostscript wget unzip

# Install sqlite3
mkdir ~/c_sqlite
wget https://www.sqlite.org/2020/sqlite-autoconf-3320200.tar.gz -P  ~/c_sqlite
cd ~/c_sqlite && tar xvzf sqlite-autoconf-3320200.tar.gz
cd ~/c_sqlite/sqlite-amalgamation-3320200 && ./

# Install PROJ4
mkdir ~/c_proj
wget http://download.osgeo.org/proj/proj-7.0.0.zip -P ~/c_proj

cd ~/c_proj && unzip proj-7.0.0.zip
cd ~/c_proj/proj-7.0.0 && ./configure # Problema com versão sqlite3
cd ~/c_proj/proj-7.0.0 && make
cd ~/c_proj/proj-7.0.0 && sudo make install

# Install GEOS
mkdir ~/c_geos
wget http://download.osgeo.org/geos/geos-3.8.0.tar.bz2 -P ~/c_geos

cd ~/c_geos && tar xfj geos-3.8.0.tar.bz2
cd ~/c_geos/geos-3.8.0 && ./configure
cd ~/c_geos/geos-3.8.0 && make
cd ~/c_geos/geos-3.8.0 && sudo make install

# Install GDAL
mkdir ~/c_gdal

wget http://s3.amazonaws.com/etc-data.koordinates.com/gdal-travisci/install-libkml-r864-64bit.tar.gz -P ~/c_gdal/
cd ~/c_gdal && tar xzf install-libkml-r864-64bit.tar.gz
sudo cp -r ~/c_gdal/install-libkml/include/* /usr/local/include
sudo cp -r ~/c_gdal/install-libkml/lib/* /usr/local/lib
sudo ldconfig

wget http://download.osgeo.org/gdal/3.0.4/gdal-3.0.4.tar.gz -P ~/c_gdal/

cd ~/c_gdal && tar xvzf gdal-3.0.4.tar.gz
cd ~/c_gdal/gdal-3.0.4 && CFLAGS="-g -Wall" LDFLAGS="-s" ./configure --with-png=internal --with-libtiff=internal --with-geotiff=internal --with-jpeg=internal  --with-gif=internal --with-ecw=no --with-expat=yes --with-sqlite3=yes --with-spatialite=yes --with-geos=yes --with-python --with-libz=internal  --with-netcdf --with-threads=yes --without-grass --without-ogdi --with-pg=/usr/bin/pg_config --with-xerces=yes
```