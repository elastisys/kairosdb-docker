#!/usr/bin/env python
from __future__ import print_function

import logging
import os
import sys
import time

from cassandra.cluster import Cluster

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")



def await_reachable(max_retries=60, retry_delay=2.0):
    """Waits for the Thrift port to become reachable for any of the
    cassandra hosts in `${CASSANDRA_HOSTS}`. Raises an error when
    `max_retries` has been exhausted.
    """
    log.info("waiting for Cassandra to become reachable ...")
    # ['host1', 'host2']
    cassandra_hosts = os.environ["CASSANDRA_HOSTS"].split(",")
    port = os.environ['CASSANDRA_PORT']
    for retry in range(max_retries):
        log.info("attempt %d at connecting to Cassandra cluster  %s (port: %s)" %
                 (retry, cassandra_hosts, port))
        try:
            cluster = Cluster(cassandra_hosts, port=port)
            cluster.connect('system')
            log.info("cluster found to be reachable")
            return
        except Exception as e:
            log.info("cassandra cluster %s not reachable: %s" %
                     (cassandra_hosts, str(e)))
        time.sleep(retry_delay)
    raise RuntimeError("gave up waiting for Cassandra to become reachable")



def exit_with_message(message):
    log.error(message)
    sys.exit(1)


kairosdb_home = os.getenv("KAIROSDB_HOME", "/opt/kairosdb")

#
# Required environment variables
#

# comma-separated list of cassandra hostnames
if not os.getenv("CASSANDRA_HOSTS"):
    exit_with_message("error: missing environment variable ${CASSANDRA_HOSTS}")
os.environ["CASSANDRA_PORT"] = os.getenv("CASSANDRA_PORT", "9042")

#
# Optional environment variables
#

# name of keyspace to crate (the keyspace is created once on first start).
os.environ["CASSANDRA_KEYSPACE"] = os.getenv("CASSANDRA_KEYSPACE", "kairosdb")
# the replication strategy to use for the Cassandra keyspace (only used the
# first time Kairos starts up and needs to create the schema in Cassandra). 
os.environ["CASSANDRA_REPLICATION"] = os.getenv("CASSANDRA_REPLICATION", "{'class': 'SimpleStrategy','replication_factor' : 1}")
# the maximum concurrency for a single metric query (that needs to run
# queries over several partitions)
os.environ["SIMULTANEOUS_CQL_QUERIES"] = os.getenv("SIMULTANEOUS_CQL_QUERIES", "20")
# the number of threads to use to read results from CQL queries
os.environ["QUERY_READER_THREADS"] = os.getenv("QUERY_READER_THREADS", "6")
# the maximum number of datapoints allowed to be returned in a single metric
# query. an attempt to fetch more datapoints in a single call will result
# in an error being returned to the client.
os.environ["QUERY_LIMIT"] = os.getenv("QUERY_LIMIT", "100000")
os.environ["CASSANDRA_READ_CONSISTENCY_LEVEL"] = os.getenv("CASSANDRA_READ_CONSISTENCY_LEVEL", "ONE")
os.environ["CASSANDRA_WRITE_CONSISTENCY_LEVEL"] = os.getenv("CASSANDRA_WRITE_CONSISTENCY_LEVEL", "QUORUM")
# time-to-live in seconds for inserted datapoints (if not set data will be
# kept forever)
os.environ["CASSANDRA_DATAPOINT_TTL"] = os.getenv("CASSANDRA_DATAPOINT_TTL", "31536000")

nodes=[h + ":" +  os.environ["CASSANDRA_PORT"]
       for h in os.environ['CASSANDRA_HOSTS'].split(',')]
os.environ['CASSANDRA_NODES'] = ','.join(nodes)

# render kairosdb config (from template and environment variables)
config_template = kairosdb_home + "/conf/kairosdb.properties.template"
config_dest = kairosdb_home + "/conf/kairosdb.properties"
with open(config_template) as template:
    with open(config_dest, "w") as dest:
        rendered_config = os.path.expandvars(template.read())
        dest.write(rendered_config)


# wait for at least one Cassandra node to become reachable before starting
# KairosDB (since kairosdb fails to start when Cassandra cannot be reached)
await_reachable()


# start kairosdb
path = kairosdb_home + "/bin/kairosdb.sh"
cmd = ["/bin/bash", "-c", path, "run"]
log.info("running: %s" % " ".join(cmd))
os.execl(*cmd)
