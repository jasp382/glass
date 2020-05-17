Install and configure geomoose:
====================


## Install GeoMoose Dependencies ##

```Bash
sudo add-apt-repository ppa:ubuntugis/ppa
sudo apt update

sudo apt install -y apache2 mapserver-bin cgi-mapserver gdal-bin

sudo apt install -y git-core unzip
```


## Install GeoMoose ##

```Bash
sudo mkdir /srv/geomoose
sudo chown ubuntu:ubuntu /srv/geomoose
cd /srv/geomoose

wget https://www.geomoose.org/downloads/gm3-examples-3.9.0.zip
wget https://www.geomoose.org/downloads/gm3-demo-data-3.9.0.zip

unzip gm3-examples-3.9.0.zip
unzip gm3-demo-data-3.9.0.zip

# Make things available in the apache document root

sudo ln -s /srv/geomoose/gm3-examples/htdocs /var/www/html/geomoose
sudo a2enmod cgi
sudo apachectl restart
```

## Setup config.js ##


Create a new config.js file in /srv/geomoose/gm3-examples/htdocs/desktop. Put the followings into config.js:

```
CONFIG = {
    mapserver_url: "/cgi-bin/mapserv",
    mapfile_root: "/srv/geomoose/gm3-demo-data/"
};
```