#!/usr/bin/env python3

import argparse
import http.client
import json
import logging
import random
import urllib.parse
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(message)s')
log = logging.getLogger(__name__)

def datapoint(datetime, value):
    t_seconds = (t - datetime.utcfromtimestamp(0)).total_seconds()
    t_millis = t_seconds * 1000
    return [ t_millis, float(value) ]

def datapoint_batch(datapoints, metric, tags=None):
    return [
        {
            "name": metric,
            "datapoints": datapoints,
            "tags": tags
        }
    ]

def send(datapoints):
    log.info("sending metric batch (ending at %s) of size %d to %s:%d",
             t, args.batch_size, args.kairosdb_host, args.kairosdb_port)
    conn = http.client.HTTPConnection(args.kairosdb_host, args.kairosdb_port)
    tags = {"host": "localhost","region": "eu-central"}
    batch = datapoint_batch(datapoints, metric='request_count', tags=tags)
    conn.request("POST", "/api/v1/datapoints", body=json.dumps(batch))
    response = conn.getresponse()
    log.info("response: {}: {}".format(response.status, response.read()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('startdate', metavar="<startdate>",
                        help="start date: YYYY-MM-dd")
    parser.add_argument('enddate', metavar="<enddate>",
                        help="end date: YYYY-MM-dd")
    parser.add_argument('--interval', metavar="SECONDS", type=int, default=10,
                        help="sampling interval (seconds). default: 10")
    parser.add_argument('--kairosdb-host', metavar="HOST", default="localhost",
                        help="kairosdb host. default: localhost")
    parser.add_argument('--kairosdb-port', metavar="PORT", type=int, default=8080,
                        help="kairosdb port. default: 8080")
    parser.add_argument('--batch-size', metavar="POINTS", type=int,
                        default=5000,
                        help="batch size (number of metric values to collect before each post). default: 5000")
    args = parser.parse_args()
    log.debug(args)

    starttime = datetime.strptime(args.startdate, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
    endtime = datetime.strptime(args.enddate, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
    log.info("start time: %s" % starttime)
    log.info("end time: %s" % endtime)


    t = starttime
    datapoints = []
    req_count = 0
    while t < endtime:
        t += timedelta(seconds=args.interval)
        req_count += random.randint(10, 30)
        datapoints.append(datapoint(t, req_count))
        if len(datapoints) >= args.batch_size:
            send(datapoints)
            datapoints = []

    if datapoints:
        send(datapoints)
