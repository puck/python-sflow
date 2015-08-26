"""
Determine the "customer" of a flow.
"""

import phpipam
import json
import ipaddr

def setup(new_config):
    global config
    global ipam

    config = new_config
    ipam = phpipam.PHPIPAM(
        config.config['plugins']['phpipam']['url'],
        config.config['plugins']['phpipam']['api_id'],
        config.config['plugins']['phpipam']['api_key']
    )

    slurp_details()


def slurp_details():
    global ipam
    global subnets
    global ips

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
    if flow['metadata']['has_ip'] == False:
        return flow

    flow['metadata']['customer']   = _address_in_network_list(flow['metadata']['local_address']) or 'unknown'

    if flow['metadata']['local_address'] in ips:
        flow['metadata']['local_name'] = ips[flow['metadata']['local_address']]
    else:
        flow['metadata']['local_name'] = flow['metadata']['local_address']

    return flow
