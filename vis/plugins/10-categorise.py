"""
Categorise the remote network type
"""

import logging
import ipaddr

def setup(new_config):
    global classified_networks
    global unclassifiable_network
    global config

    config = new_config

    # networks which will get a particular classification
    try:
        classified_networks = {classification: _load_networks_from_file(networks) for classification, networks in config.config['plugins']['categorise']['classifications'].iteritems() }
        unclassifiable_network = config.config['plugins']['categorise']['unclassifiable'] # fall back if no classification possible
    except:
        raise Exception("unable to load network classifications")


def _load_networks_from_file(filename):
    """
    Load a list of IPv4 and IPv6 networks from filename and return a list of
    IPNetwork objects corresponding to any valid networks in the file.
    """

    networks = []
    print "considering: %s" % filename

    with open(filename, 'r') as fp:
        for line in fp:

            # validate network by parsing it and skip if it doesn't validate
            try:
                networks.append(ipaddr.IPNetwork(line.strip()))
            except:
                continue

    logging.info("loaded %i networks from %s" % (len(networks), filename))

    return networks

def _address_in_network_list(address, networks):
    """
    Returns true if address is within any of the networks.
    """

    return any([ipaddr.IPAddress(address) in network for network in networks])

def mangle_flow(flow):
    global classified_networks
    global unclassifiable_network

    if flow['metadata']['has_ip'] == False:
        return flow

    
    billing = None

    # determine which billing class the packet belongs to, if any
    for network_class, networks_in_class in classified_networks.iteritems():
        if _address_in_network_list(flow['metadata']['remote_address'], networks_in_class):
            billing = network_class
            break

    if not billing:
        billing = unclassifiable_network

    flow['metadata']['billing'] = billing

    return flow
