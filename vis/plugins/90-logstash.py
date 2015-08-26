"""
Send packets to logstash!
"""

import json
import datetime
import os
import logging

config  = None
logstash_current = None
logstash_file    = None

def setup(new_config):
    global config
    global logfile

    config = new_config

    logfile = config.config['plugins']['logstash']['logfile']
    if logfile is None:
        logfile = "/var/spool/python-sflow/sflow-logstash.log"

def mangle_flow(flow):
    global logfile
    global logstash_file
    global logstash_current
    logger = logging.getLogger(__name__)

    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    if logstash_current is None or today != logstash_current:
        logstash_current = today
        try:
            logstash_file.close()
        except:
            pass

        logfile_current = "%s.%s" % (logfile, logstash_current)
        print "logfile to use: %s" % (logfile_current)
        logstash_file = open(logfile_current, 'wb')

    now = datetime.datetime.utcnow();
    json_body = {
            "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (now.microsecond / 1000) + "Z",
            "sflow": flow['metadata'],
            "packets": flow['sample']['sampling_rate'],
            "octets": (flow['frame_length'] - flow['stripped'] - flow['header_length']) * flow['sample']['sampling_rate'],
        }

    if 'remote_address' in flow['metadata']:
        json_body["clientip"] = flow['metadata']['remote_address']


    logstash_file.write(json.dumps(json_body, sort_keys = True, ensure_ascii=False) + "\n")
    return flow
