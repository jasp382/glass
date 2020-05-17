GLASS | Setup development environment:
================

### Clone undersee-webgis repository:

```
sudo apt install git

mkdir ~/code
git clone https://github.com/jasp382/glass ~/code/glass
```

### Install dependencies:

* [Ubuntu 18.04](dependencies/ub18.md);

* [Ubuntu 20.04](dependencies/ub20.md);

* [MacOS](dependencies/macos.md);


### Setup Python virtual environment:

```
# Create new virtual env
mkvirtualenv glassenv
workon glassenv

# Install USEEGIS
cd ~/code/glass/core && pip install -r requirements.txt
gv=$(ogr2ogr --version)
gvv="${gv:5:-21}"
pip install pygdal==$gvv.6

pv=$(/usr/bin/python3 --version)
pvv="${pv:7:-2}"
echo "/home/$USER/code/glass/core" | sudo tee ~/.virtualenvs/glassenv/lib/python$pvv/site-packages/glass.pth
```