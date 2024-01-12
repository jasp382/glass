Install Web Dependencies:
====================

## Install NodeJS and NPM: ##

```
wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.39.2/install.sh | bash

source ~/.profile

nvm install 20.11.0
```


## Install Angular globaly: ##

```
npm install -g @angular/cli
```

## Install GeoServer: ##

**1 - Install Apache2:**

```
sudo apt install apache2 libapache2-mod-wsgi-py3
sudo a2enmod rewrite
sudo a2enmod ssl
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_ajp
```

**2 - Install Tomcat:**

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

mkdir ~/geoserver_inst && sudo wget http://sourceforge.net/projects/geoserver/files/GeoServer/2.24.2/geoserver-2.24.2-war.zip -P ~/geoserver_inst/

sudo unzip ~/geoserver_inst/geoserver-2.24.2-war.zip -d ~/geoserver_inst/

sudo mv ~/geoserver_inst/geoserver.war /var/lib/tomcat9/webapps/

sudo service apache2 restart
sudo service tomcat9 restart
```
