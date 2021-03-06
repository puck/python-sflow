"""
Determine the "customer" of a flow.
"""

import phpipam
import json
import ipaddr
import time

def setup(new_config):
    global config
    global ipam
    global ipam_next_reload

    config = new_config
    ipam = phpipam.PHPIPAM(
        config.config['plugins']['phpipam']['url'],
        config.config['plugins']['phpipam']['api_id'],
        config.config['plugins']['phpipam']['api_key']
    )

    slurp_details()


def slurp_details():
    global config
    global ipam
    global subnets
    global ips
    global ipam_next_reload

    subnets = []
    ips     = {}

    data = json.loads(ipam.read_subnets())
    for subnet in data['data']:
        if subnet['subnet'] == '0.0.0.0':
            continue

        subnets.append([ipaddr.IPNetwork(subnet['subnet'] + '/' + subnet['mask']), subnet['description']])

        ip_data = json.loads(ipam.read_addresses(subnet_id=subnet['id']))
        if ip_data['success']:
            for ip in ip_data['data']:
                ips[ip['ip_addr']] = ip['description'] or ip['dns_name']

    print "phpipam: loaded %d subnets, %d IP addresses" % (len(subnets), len(ips))

    # Default to a reload_interval of 30 minutes
    try:
        reload_interval = config.config['plugins']['phpipam']['reload_interval']
    except:
        reload_interval = 30
    ipam_next_reload = int(time.time()) + 60 * reload_interval

def _address_in_network_list(address):
    """
    Returns the description for the most specific network which contains address
    """
    global subnets

    description = None
    prefixlen = None
    for subnet in subnets:
        if ipaddr.IPAddress(address) in subnet[0]:
            if prefixlen is None or subnet[0].prefixlen > prefixlen:
                description = subnet[1]
                prefixlen = subnet[0].prefixlen

    return description

def mangle_flow(flow):
    global ipam_next_reload

    if flow['metadata']['has_ip'] == False:
        return flow

    if ipam_next_reload <= int(time.time()):
        print "phpipam: reloading details"
        slurp_details()

    flow['metadata']['customer']   = _address_in_network_list(flow['metadata']['local_address']) or 'unknown'

    if flow['metadata']['local_address'] in ips:
        flow['metadata']['local_name'] = ips[flow['metadata']['local_address']]
    else:
        flow['metadata']['local_name'] = flow['metadata']['local_address']

    return flow
