# Setup Local GeoNode Instance (2023) #

### Setup Docker

# install OS level packages..
sudo add-apt-repository universe
sudo apt-get update -y
sudo apt-get install -y git-core git-buildpackage debhelper devscripts python3.10-dev python3.10-venv virtualenvwrapper
sudo apt-get install -y apt-transport-https ca-certificates curl lsb-release gnupg gnupg-agent software-properties-common vim

# add docker repo and packages...
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose
sudo apt autoremove --purge

# add your user to the docker group...
sudo usermod -aG docker ${USER}
su ${USER}

### Clone GeoNode

# Let's create the GeoNode core base folder and clone it
sudo mkdir -p /opt/geonode/
sudo usermod -a -G www-data geonode
sudo chown -Rf geonode:www-data /opt/geonode/
sudo chmod -Rf 775 /opt/geonode/

# Clone the GeoNode source code on /opt/geonode
cd /opt
git clone https://github.com/GeoNode/geonode.git

### Prepare .env file

cd /opt/geonode && python3 create-envfile.py

### Build and run
docker compose build
docker compose up -d