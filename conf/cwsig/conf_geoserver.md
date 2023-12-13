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

## 2 - Install GeoServer: ##

**2.1 - Install Apache2:**

```
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

