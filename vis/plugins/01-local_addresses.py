"""
Determine the "direction" of a flow.
"""

def mangle_flow(flow):
    if flow['metadata']['has_ip'] == False:
        return flow

    if flow['sample']['input'] == 0x3FFFFFFF: # sflow interface "internal"
        flow['metadata']['direction'] = 'outbound'
        flow['metadata']['local_address'] = flow['metadata']['source_ip']
        flow['metadata']['remote_address'] = flow['metadata']['destination_ip']
    else:
        flow['metadata']['direction'] = 'inbound'
        flow['metadata']['local_address'] = flow['metadata']['destination_ip']
        flow['metadata']['remote_address'] = flow['metadata']['source_ip']

    flow['metadata'].pop('source_ip')
    flow['metadata'].pop('destination_ip')

    return flow
