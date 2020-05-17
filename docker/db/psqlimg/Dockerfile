FROM ubuntu:focal

LABEL version="1.0"
LABEL description="Image with PostgreSQL/PostGIS installed"
LABEL maintainer="Joaquim Patriarca<jpatriarca@mat.uc.pt>"

RUN apt-get -qq update --fix-missing && apt-get -qq --yes upgrade

RUN set -eux \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get -y --no-install-recommends install \
        locales gnupg2 wget ca-certificates rpl pwgen software-properties-common  iputils-ping \
        apt-transport-https ca-certificates curl \
    && apt-get -y --purge autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && dpkg-divert --local --rename --add /sbin/initctl

# Generating locales takes a long time. Utilize caching by runnig it by itself
# early in the build process.
RUN curl https://deb.meteo.guru/velivole-keyring.asc | apt-key add - \
    && apt-get update ; sh -c "echo \"deb https://deb.meteo.guru/debian focal main\" > /etc/apt/sources.list.d/meteo.guru.list"

RUN apt-get -y update; apt-get -y install build-essential autoconf  libxml2-dev zlib1g-dev netcat gdal-bin

COPY locale.gen /etc/locale.gen
RUN set -eux \
    && /usr/sbin/locale-gen

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8
RUN update-locale ${LANG}

# Cleanup resources
RUN apt-get -y --purge autoremove  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Reset ARG for version
ARG POSTGRES_MAJOR_VERSION=12
ARG POSTGIS_MAJOR=3

# Setup PostgreSQL repository

RUN set -eux \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get upgrade;apt-get update \
    && sh -c "echo \"deb http://apt.postgresql.org/pub/repos/apt/ focal-pgdg main\" > /etc/apt/sources.list.d/pgdg.list" \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc -O- | apt-key add - \
    && apt-get -y --purge autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && dpkg-divert --local --rename --add /sbin/initctl

# Install PostgreSQL and PostGIS

# We add postgis as well to prevent build errors (that we dont see on local builds)
# on docker hub e.g.
# The following packages have unmet dependencies:
RUN set -eux \
    && export DEBIAN_FRONTEND=noninteractive \
    &&  apt-get update \
    && apt-get -y --no-install-recommends install postgresql-client-${POSTGRES_MAJOR_VERSION} \
        postgresql-common postgresql-${POSTGRES_MAJOR_VERSION} \
        postgresql-${POSTGRES_MAJOR_VERSION}-postgis-${POSTGIS_MAJOR} \
        netcat postgresql-${POSTGRES_MAJOR_VERSION}-ogr-fdw \
        postgresql-${POSTGRES_MAJOR_VERSION}-postgis-${POSTGIS_MAJOR}-scripts \
        postgresql-plpython3-${POSTGRES_MAJOR_VERSION} postgresql-${POSTGRES_MAJOR_VERSION}-pgrouting \
        postgresql-server-dev-${POSTGRES_MAJOR_VERSION} postgresql-${POSTGRES_MAJOR_VERSION}-cron

RUN echo $POSTGRES_MAJOR_VERSION >/tmp/pg_version.txt

# Compile pointcloud extension
RUN wget -O- https://github.com/pgpointcloud/pointcloud/archive/master.tar.gz | tar xz && \
cd pointcloud-master && \
./autogen.sh && ./configure && make -j 4 && make install && \
cd .. && rm -Rf pointcloud-master

# Cleanup resources
RUN apt-get -y --purge autoremove  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose PostgreSQL PORT
EXPOSE 5432