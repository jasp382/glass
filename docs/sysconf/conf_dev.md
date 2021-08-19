GLASS | Setup development environment:
================

### Clone glass repository:

```
sudo apt install git

mkdir ~/code
git clone https://github.com/jasp382/glass ~/glass
```

### Install dependencies:

* [Ubuntu 18.04](dep/ub18.md);

* [Ubuntu 20.04](dep/ub20.md);

* [MacOS](dep/macos.md);


### Setup Python virtual environment:

```
# Create new virtual env
mkvirtualenv glassenv
workon glassenv

# Install GLASS
cd ~/glass/core && pip install -r requirements.txt
gv=$(ogr2ogr --version)
gvv="${gv:5:-21}"
pip install pygdal==$gvv.6

pv=$(/usr/bin/python3 --version)
pvv="${pv:7:-2}"
echo "/home/$USER/glass/core" | sudo tee ~/.virtualenvs/glassenv/lib/python$pvv/site-packages/glass.pth
```