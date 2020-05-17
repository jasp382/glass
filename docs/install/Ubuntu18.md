Install GASP Dependencies in Ubuntu 18.04
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

### 3 - Install PostgreSQL and PostGIS:

```
sudo apt install postgis
```
	
**PostGIS basic configuration:**

```
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'admin';"
sudo -u postgres psql -c "CREATE EXTENSION postgis;"
sudo -u postgres psql -c "CREATE EXTENSION postgis_topology;"
sudo -u postgres createdb postgis_template
sudo -u postgres psql -d postgis_template -c "UPDATE pg_database SET datistemplate=true WHERE datname='postgis_template'"
sudo -u postgres psql -d postgis_template -c "CREATE EXTENSION hstore;"
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/postgis.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/postgis_comments.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/spatial_ref_sys.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/rtpostgis.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/raster_comments.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/topology.sql
sudo -u postgres psql -d postgis_template -f /usr/share/postgresql/10/contrib/postgis-3.0/topology_comments.sql
```

### 4 - Install OSMIUM and OSMOSIS:

```
sudo apt install osmium-tool
sudo apt install osmosis
```

### 5 - Install SAGA GIS (optional):

```
sudo apt install libwxgtk3.0-dev libtiff5-dev libexpat-dev wx-common unixodbc-dev

sudo apt install g++ make automake libtool git

# Downloading SAGA sources
cd ~
git clone git://git.code.sf.net/p/saga-gis/code saga-gis-code

# Compile SAGA
cd saga-gis-code/saga-gis
autoreconf -fi
	
./configure
make
sudo make install
```