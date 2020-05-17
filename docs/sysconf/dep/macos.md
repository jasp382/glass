GLASS | Install GLASS dependencies in MacOS:
====================


## 1 - Setup HomeBrew:

Install HomeBrew

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Open bash_profile

```
nano ~/.bash_profile
```

Write the following line, close and save

```
export PATH=/usr/local/bin:$PATH
```

Activate changes

```
source ~/.bash_profile
```

We can make sure that Homebrew was successfully installed by typing

```
brew doctor
```

## 2 - Install Python, PIP and Virtualenv

```
brew install python3

echo "export PATH=/usr/local/share/python:$PATH" | tee -a ~/.bash_profile

pip3 install --ugrade pip

pip3 install virtualenv virtualenvwrapper

echo "export WORKON_HOME=$HOME/.virtualenvs" | tee -a ~/.zshrc
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3" | tee -a ~/.zshrc
echo "export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv" | tee -a ~/.zshrc
echo "source /usr/local/bin/virtualenvwrapper.sh" | tee -a ~/.zshrc

source ~/.bash_profile
source ~/.zshrc
```

## 3 - Install GDAL:

```
brew install gdal --HEAD
brew install gdal
```

**Set GDAl environment variables:**

```
echo "export GDAL_DATA=/usr/local/share/gdal" | tee -a ~/.bash_profile
echo "export PROJ_LIB=/usr/local/share/proj" | tee -a ~/.bash_profile

source ~/.bash_profile
```

## 4 - Install PostgreSQL and PostGIS:

```
brew install postgres
brew services start postgresql

brew install postgis
```

**PostGIS basic configuration:**

```
psql -U $USER -d postgres -c "ALTER USER $USER PASSWORD 'admin';"
createdb postgis_template
psql -U $USER -d postgis_template -c "CREATE EXTENSION postgis;"
psql -U $USER -d postgis_template -c "CREATE EXTENSION postgis_topology;"
psql -U $USER -d postgis_template -c "UPDATE pg_database SET datistemplate=true WHERE datname='postgis_template'"
psql -U $USER -d postgis_template -c "CREATE EXTENSION hstore;"
psql -U $USER -d postgis_template -f /usr/local/share/postgis/postgis.sql
psql -U $USER -d postgis_template -f /usr/local/share/postgis/postgis_comments.sql
psql -U $USER -d postgis_template -f /usr/local/share/postgis/spatial_ref_sys.sql
psql -U $USER -d postgis_template -f /usr/local/share/postgis/rtpostgis.sql
psql -U $USER -d postgis_template -f /usr/local/share/postgis/raster_comments.sql
psql -U $USER -d postgis_template -f /usr/local/share/postgis/topology.sql
psql -U $USER -d postgis_template -f /usr/local/share/postgis/topology_comments.sql
```

## 5 - Install Apach2, Tomcat and GeoServer:

**5.1. - Install Java:**

```
brew update
brew install java

echo 'export PATH="/usr/local/opt/openjdk/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**5.2. - Install Tomcat:**

```
brew install tomcat
brew services start tomcat
```

**5.3. - Install GeoServer:**

```
brew install gnutls

cd ~/Downloads && curl -O https://ftp.gnu.org/gnu/wget/wget-1.19.5.tar.gz
cd ~/Downloads && tar -zxvf wget-1.19.5.tar.gz
cd ~/Downloads/wget-1.19.5 && ./configure
cd ~/Downloads/wget-1.19.5 && make
cd ~/Downloads/wget-1.19.5 && make install

mkdir ~/geoserver_inst
wget http://sourceforge.net/projects/geoserver/files/GeoServer/2.18.1/geoserver-2.18.1-war.zip -P ~/geoserver_inst/

unzip ~/geoserver_inst/geoserver-2.18.1-war.zip -d ~/geoserver_inst/

mv ~/geoserver_inst/geoserver.war /usr/local/Cellar/tomcat/9.0.41/libexec/webapps/

brew services restart tomcat
```