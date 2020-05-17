FROM psqlimg

LABEL version="1.0"
LABEL description="Run PostgreSQL/PostGIS container"
LABEL maintainer="Joaquim Patriarca<jpatriarca@mat.uc.pt>"

# Copy scripts
ADD ./scripts /scripts
WORKDIR /scripts
RUN chmod +x *.sh

# Run any additional tasks here that are too tedious to put in
# this dockerfile directly.
RUN set -eux \
    && /scripts/setup.sh

VOLUME /var/lib/postgresql

ENTRYPOINT /scripts/docker-entrypoint.sh