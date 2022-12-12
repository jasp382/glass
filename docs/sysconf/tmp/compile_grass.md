# be sure to have an updated system
sudo apt-get update && sudo apt-get upgrade -y

# install PROJ
sudo apt-get install libproj-dev proj-data proj-bin unzip -y

# install GEOS
sudo apt-get install libgeos-dev -y

# install GDAL
sudo apt-get install libgdal-dev python3-gdal gdal-bin -y

# install PDAL (optional)
sudo apt-get install libpdal-dev pdal libpdal-plugin-python -y

# recommended to give Python3 precedence over Python2 (which is end-of-life since 2019)
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Install dependencies:

```
sudo apt-get install build-essential flex make bison gcc libgcc1 g++ ccache python3 python3-dev python3-opengl python3-wxgtk4.0 python3-dateutil libgsl-dev python3-numpy wx3.0-headers wx-common libwxgtk3.0-gtk3-dev libwxbase3.0-dev libncurses5-dev libbz2-dev zlib1g-dev gettext libtiff5-dev libpnglite-dev libcairo2 libcairo2-dev sqlite3 libsqlite3-dev  libpq-dev libreadline6-dev libfreetype6-dev libfftw3-3 libfftw3-dev libboost-thread-dev libboost-program-options-dev  libpdal-dev subversion libzstd-dev checkinstall libglu1-mesa-dev libxmu-dev ghostscript wget -y
```

# Download GRASS GIS:

```
wget https://github.com/OSGeo/grass/archive/refs/tags/7.8.7.tar.gz
tar -xzvf 7.8.7.tar.gz
cd grass-7.8.7

```

# "configure" source code for local machine (checks for CPU type etc):
MYCFLAGS='-O2 -fPIC -fno-common -fexceptions -std=gnu99 -fstack-protector -m64'
#MYCXXFLAGS=''
MYLDFLAGS='-Wl,--no-undefined -Wl,-z,now'

LDFLAGS="$MYLDFLAGS" CFLAGS="$MYCFLAGS" CXXFLAGS="$MYCXXFLAGS" ./configure \
  --with-cxx \
  --enable-largefile \
  --with-proj --with-proj-share=/usr/share/proj \
  --with-gdal=/usr/bin/gdal-config \
  --with-python \
  --with-geos \
  --with-sqlite \
  --with-nls \
  --with-zstd \
  --with-pdal \
  --with-cairo --with-cairo-ldflags=-lfontconfig \
  --with-freetype=yes --with-freetype-includes="/usr/include/freetype2/" \
  --with-wxwidgets \
  --with-fftw \
  --with-motif \
  --with-opengl-libs=/usr/include/GL \
  --with-postgres=yes --with-postgres-includes="/usr/include/postgresql" \
  --without-netcdf \
  --without-mysql \
  --without-odbc \
  --without-openmp \
  --without-ffmpeg

# note: the more CPUs you have, the higher the -j number may be set to
# here: build using 4 CPU cores
make -j4

sudo make install