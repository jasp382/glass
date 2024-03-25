Setup GeoServer, GeoNode and GeoMoose
================


### 1 - Install dependencies: ###


```Bash
sudo add-apt-repository universe
sudo apt-get update -y
sudo apt-get install -y git-core git-buildpackage debhelper devscripts python3.10-dev python3.10-venv virtualenvwrapper
sudo apt-get install -y apt-transport-https ca-certificates curl lsb-release gnupg gnupg-agent software-properties-common vim
```


### 2 - Install Docker: ###

```Bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose
sudo apt autoremove --purge

sudo usermod -aG docker ${USER}
su ${USER}
```

## 3 - Install GDAL: ##

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

## 4 - Install GeoServer: ##

**2.1 - Install Apache2:**

```Bash
sudo apt install apache2 libapache2-mod-wsgi-py3
sudo a2enmod rewrite
sudo a2enmod ssl
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_ajp
```

**2.2 - Install Tomcat:**

```
# Install Java
sudo apt install default-jdk

echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" | sudo tee --append ~/.bashrc
source ~/.bashrc

# Tomcat 9
sudo apt install tomcat9 tomcat9-admin -y
```

**Add new user to tomcat-users.xml**

Edit /etc/tomcat9/tomcat-users.xml and add the following line:

```
<user username="useriam" password="useriam" roles="manager-gui,admin-gui" />
```


**2.3 - Install GeoServer:**

```
sudo apt install unzip

mkdir ~/geoserver_inst && sudo wget http://sourceforge.net/projects/geoserver/files/GeoServer/2.23.1/geoserver-2.23.1-war.zip -P ~/geoserver_inst/

sudo unzip ~/geoserver_inst/geoserver-2.23.1-war.zip -d ~/geoserver_inst/

sudo mv ~/geoserver_inst/geoserver.war /var/lib/tomcat9/webapps/

sudo service apache2 restart
sudo service tomcat9 restart
```

## 5 - Install GeoNode: ##


```Bash
# Let's create the GeoNode core base folder and clone it
sudo mkdir -p /opt/geonode/
sudo usermod -a -G www-data cwsig
sudo chown -Rf cwsig:www-data /opt/geonode/
sudo chmod -Rf 775 /opt/geonode/

# Clone the GeoNode source code on /opt/geonode
cd /opt
git clone https://github.com/GeoNode/geonode.git

### Prepare .env file

cd /opt/geonode && python3 create-envfile.py

### Build and run
docker compose build
docker compose up -d
```


## 6 - Install GeoMoose: ##

```Bash
sudo add-apt-repository ppa:ubuntugis/ppa

sudo apt update

sudo apt install -y mapserver-bin cgi-mapserver gdal-bin

sudo apt install -y git-core unzip


sudo mkdir /srv/geomoose
sudo chown cwsig:cwsig /srv/geomoose
cd /srv/geomoose

wget https://www.geomoose.org/downloads/gm3-examples-3.10.1.zip
wget https://www.geomoose.org/downloads/gm3-demo-data-3.10.1.zip

unzip gm3-examples-3.10.1.zip
unzip gm3-demo-data-3.10.1.zip

# Make things available in the apache document root

sudo ln -s /srv/geomoose/gm3-examples/htdocs /var/www/html/geomoose
sudo a2enmod cgi
sudo apachectl restart

## Setup config.js ##


Create a new config.js file in /srv/geomoose/gm3-examples/htdocs/desktop. Put the followings into config.js:

```
CONFIG = {
    mapserver_url: "/cgi-bin/mapserv",
    mapfile_root: "/srv/geomoose/gm3-demo-data/"
};
```