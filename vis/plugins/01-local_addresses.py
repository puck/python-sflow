"""
Determine the "direction" of a flow.
"""

def setup(new_config):
    global config

    config = new_config

def mangle_flow(flow):
    if flow['metadata']['has_ip'] == False:
        return flow

    # Hack to make it opposite for the Catalyst Office network
    if flow['sample']['input'] == 0x3FFFFFFF and config.config['local'] == 'inbound':
        # sflow interface "internal"
        flow['metadata']['direction'] = 'inbound'
        flow['metadata']['local_address']  = flow['metadata']['destination_ip']
        flow['metadata']['remote_address'] = flow['metadata']['source_ip']
        flow['metadata']['local_mac']  = flow['metadata']['source_mac']
        flow['metadata']['remote_mac'] = flow['metadata']['destination_mac']
    else:
        flow['metadata']['direction'] = 'outbound'
        flow['metadata']['local_address'] = flow['metadata']['source_ip']
        flow['metadata']['remote_address'] = flow['metadata']['destination_ip']
        flow['metadata']['local_mac']  = flow['metadata']['destination_mac']
        flow['metadata']['remote_mac'] = flow['metadata']['source_mac']

    flow['metadata'].pop('source_ip')
    flow['metadata'].pop('destination_ip')
    flow['metadata'].pop('source_mac')
    flow['metadata'].pop('destination_mac')

    return flow
