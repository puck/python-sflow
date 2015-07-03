"""
Look for signs for a pernicious APT (n.b. this plugin is a joke).
"""

def mangle_flow(flow):
    if 'User-Agent: X' in flow['payload']: # OH NO, THE APT HAS PERVERTED THE PACKET!
        flow['metadata']['dissident'] = 'yep'
    else:
        flow['metadata']['dissident'] = 'nah'

    if 'metlstorm' in flow['payload']:
        flow['metadata']['suspicious'] = 'yep'
    else:
        flow['metadata']['suspicious'] = 'nah'

    return flow
