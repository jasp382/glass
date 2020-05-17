Install glass Dependencies in Ubuntu 22.04
====================

## 1- Install Miniconda ##

```Bash
cd ~ && wget https://repo.anaconda.com/miniconda/Miniconda3-py310_23.11.0-2-Linux-x86_64.sh

sudo chmod +x Miniconda3-py310_23.11.0-2-Linux-x86_64.sh

./Miniconda3-py310_23.11.0-2-Linux-x86_64.sh

echo 'export PATH=$PATH:/home/'"$USER/miniconda3/bin" | sudo tee --append ~/.bashrc
source ~/.bashrc

conda init
```

## 2 - Create new Virtual Environment ##

```
conda create -n gs python=3.10

conda activate gs
```

## 3 - Install QGIS ##

(it will install almost everything we need)

```Bash
conda install -c conda-forge qgis=3.28
```

## 4 - Setup PostgreSQL and PostGIS ##

```Bash
conda install -c conda-forge postgis
conda install -c conda-forge pgrouting

# Start postgres server
initdb -D mylocal_db

pg_ctl -D mylocal_db -l logfile start

# Create user
createuser --encrypted --pwprompt --superuser postgres

# Create default DB
createdb --owner=postgres postgres

# Setup PostGIS
psql -U postgres -c "CREATE EXTENSION postgis;"
psql -U postgres -c "CREATE EXTENSION postgis_topology;"

createdb -U postgres postgis_template

psql -U postgres -d postgis_template -c "UPDATE pg_database SET datistemplate=true WHERE datname='postgis_template'"
psql -U postgres -d postgis_template -c "CREATE EXTENSION hstore"
psql -U postgres -d postgis_template -c "CREATE EXTENSION tablefunc"
psql -U postgres -d postgis_template -c "CREATE EXTENSION postgis"
psql -U postgres -d postgis_template -c "CREATE EXTENSION postgis_raster"
psql -U postgres -d postgis_template -c "CREATE EXTENSION postgis_topology"
psql -U postgres -d postgis_template -c "CREATE EXTENSION pgrouting"
```


## 5 - Setup GLASS ##


```Bash
git clone https://github.com/jasp382/glass ~/glass

# Install dependencies
conda install anaconda::numpy anaconda::psycopg2 anaconda::sqlalchemy conda-forge::geoalchemy2 conda-forge::shapely conda-forge::fiona conda-forge::pyproj anaconda::pandas conda-forge::geopandas conda-forge::dask-geopandas conda-forge::rasterio conda-forge::netcdf4
pip install xlrd xlwt
conda install conda-forge::xlsxwriter conda-forge::openpyxl conda-forge::dbf conda-forge::requests conda-forge::requests-oauthlib conda-forge::requests-toolbelt
pip install flickrapi==2.4.0
conda install anaconda::scipy anaconda::scikit-learn anaconda::scikit-image conda-forge::scikit-learn-intelex conda-forge::pyexcel-ods3 conda-forge::bs4 anaconda::seaborn conda-forge::sentinelsat
pip install simpledbf 
conda install conda-forge::jupyterlab conda-forge::geopy conda-forge::pysal conda-forge::rioxarray conda-forge::xmltodict
```