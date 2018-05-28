## A KairosDB Docker image
This directory contains a `Dockerfile` and some additional source files
needed to build a Docker image for KairosDB. The kairosdb container
operates against a back-end Cassandra database cluster. The Cassandra
nodes are passed to the container on launch.

Cassandra nodes can, for example, be started via the
[official Cassandra Docker image](https://hub.docker.com/_/cassandra/):

    docker run --name cassandra -d -v cassandra-data:/var/lib/cassandra -p 9042:9042 cassandra:3.11



### Building the docker image
To build the Docker image, issue the following command (possibly after
updating the `VERSION` variable):

    ./build.sh

To also push to Docker hub, do

    export PUSH=yes
	./build.sh



### Running a container from the image
Once the docker image is built for the KairosDB server, it can be run with:

    docker run -d --name kairosdb -p 4242:4242 -p 8080:8080 -e CASSANDRA_HOSTS="<hostname/ip>" elastisys/kairosdb:1.2.1

Note that a comma-separated list of back-end Cassandra hosts need to be passed
through the `CASSANDRA_HOSTS` environment variable.

This will publish the KairosDB's Telnet port on 4242 and HTTP port on 8080.

There are a number of options that can be used to control the behavior of
KairosDB. For example, you can set a replication strategy that suits your
Cassandra cluster via the `CASSANDRA_REPLICATION` environment variable (defaults
to `{'class': 'SimpleStrategy','replication_factor' : 1}`). Refer to the
[entrypoint.py](entrypoint.py) code for details.
