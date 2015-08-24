"""
Determine the "customer" of a flow.
"""

import requests, json

def setup(new_config):
    global config
    
    config = new_config

def mangle_flow(flow):
    global config

    if flow['metadata']['has_ip'] == False:
        return flow

    url = config.config['plugins']['phpipam']['url'] + "/subnets/cidr/" + flow['metadata']['local_address'] + "/32"
    print "url: %s" % url
    r = requests.post(url, None,
        auth=(config.config['plugins']['phpipam']['username'],
              config.config['plugins']['phpipam']['password']))
    print "code: %d" % r.status_code

    if r.status_code == 200:
        print "response: " + r.json()

    #flow['metadata']['customer'] = customers.get(flow['metadata']['local_address'], 'other')

    return flow
