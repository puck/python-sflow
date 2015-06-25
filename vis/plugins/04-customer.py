"""
Determine the "customer" of a flow.
"""

def mangle_flow(flow):
    if flow['metadata']['has_ip'] == False:
        return flow

    customers = {
        '192.168.0.2': 'linux-lover',
        '192.168.0.7': 'spam-sender',
    }

    flow['metadata']['customer'] = customers.get(flow['metadata']['local_address'], 'other')

    return flow
