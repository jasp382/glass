FROM ubuntu:focal
LABEL version="1.0"
LABEL description="GLASS API to production"
LABEL maintainer="Joaquim Patriarca<jpatriarca@mat.uc.pt>"

# Install dependencies
RUN apt-get update
RUN apt-get install -y tzdata nano
RUN apt-get install -y software-properties-common git
RUN apt-get install -y apt-utils vim curl apache2 apache2-utils
RUN apt-get install -y python3 libapache2-mod-wsgi-py3 
RUN ln /usr/bin/python3 /usr/bin/python 
RUN apt-get -y install python3-pip
RUN ln /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip
RUN pip install ptvsd

RUN apt-get install -y gdal-bin
RUN apt-get install -y libgdal-dev

# Add useegis folder
ADD ./glass /glass

# Install pygdal
RUN pip install pygdal==3.0.4.6

# Install GLASS
RUN cd /useegis && pip install -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/glass"

# Set glass constant values
RUN rm /glass/glass/cons/con-postgresql.json
ADD ./confiles/con-postgresql.json /glass/glass/cons

# Setup PGPASSFILE
ADD ./confiles/pgpass.conf /var/www/html
RUN export PGPASSFILE=/var/www/html/pgpass.conf

# Setup Apache
ADD ./requirements.txt /var/www/html
ADD ./undersee /var/www/html/glass
RUN rm /var/www/html/glass/ctx.json
ADD ./confiles/ctx.json /var/www/html/glass
ADD ./conf_apache.py /var/www/html

WORKDIR /var/www/html
RUN python conf_apache.py --docker -p http
RUN cp undersee/000-default.conf /etc/apache2/sites-available/000-default.conf

RUN pip install -r requirements.txt
RUN chmod 775 /var/www/html/glass/glass
RUN chmod 775 /var/www/html/glass/logs
RUN chmod -R 777 /var/www/html/glass/sdi/views/gsrvtmp
RUN chown :www-data /var/www/html/glass/glass
RUN chown :www-data /var/www/html/glass/logs

# Prepare things to restore database and GeoServer data
ADD ./restore_db.py /var/www/html
ADD ./restore_gsrv.py /var/www/html
ADD ./dbdumps /var/www/html/dbdumps

EXPOSE 80 3500 
CMD ["apache2ctl", "-D", "FOREGROUND"]