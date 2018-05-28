FROM openjdk:8-jre-alpine
MAINTAINER Elastisys <techteam@elastisys.com>  

ENV KAIROSDB_VERSION="1.2.1"
ENV VERSION_QUALIFIER="-1"
ENV DOWNLOAD_URL="https://github.com/kairosdb/kairosdb/releases/download/v${KAIROSDB_VERSION}/kairosdb-${KAIROSDB_VERSION}${VERSION_QUALIFIER}.tar.gz"

# install bash shell and python in alpine linux
RUN apk add --no-cache bash python py-pip \
    && pip install 'cassandra-driver==3.14.0' \
    && apk del py-pip \
    && rm -rf /var/cache/apk


## Install KairosDB
RUN set -e \
    && mkdir -p /opt \
    && wget ${DOWNLOAD_URL} -O /opt/kairosdb.tar.gz \
    && tar xzf /opt/kairosdb.tar.gz -C /opt/ \
    && rm /opt/kairosdb.tar.gz

COPY conf/kairosdb.properties.template /opt/kairosdb/conf/kairosdb.properties.template
COPY conf/logging/logback.xml /opt/kairosdb/conf/logging/logback.xml
COPY entrypoint.py /opt/entrypoint.py

EXPOSE 4242 8080
CMD ["/usr/bin/python", "/opt/entrypoint.py"]
