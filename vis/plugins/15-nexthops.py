"""
Categorise the remote network type
"""

import logging
import csv

def setup(new_config):
    global classified_nexthops
    global unclassifiable_nexthop
    global config

    config = new_config

    # networks which will get a particular classification
    try:
        classified_nexthops = _load_nexthops_from_file(config.config['plugins']['nexthops']['upstreams'])
        unclassifiable_nexthop = config.config['plugins']['nexthops']['unclassifiable'] # fall back if no classification possible
    except Exception,e:
        raise Exception("unable to load nexthop classifications: %s" % e)


def _load_nexthops_from_file(filename):
    """
    Load a list of nexthops from filename and return a list of MAC -> nexthops
    """

    nexthops = {}
    print "nexthops considering: %s" % filename

    with open(filename, 'r') as fp:
        nexthopreader = csv.DictReader(fp)
        for row in nexthopreader:
            nexthops[row['MAC'].lower()] = row['Name']


    logging.info("loaded %i nexthops from %s" % (len(nexthops), filename))

    return nexthops

def mangle_flow(flow):
    global classified_nexthops
    global unclassifiable_nexthop

    if flow['metadata']['has_ip'] == False:
        return flow

    nexthop = classified_nexthops[flow['metadata']['remote_mac'].lower()]

    if not nexthop:
        nexthop = unclassifiable_nexthop

    flow['metadata']['nexthop'] = nexthop

    return flow
