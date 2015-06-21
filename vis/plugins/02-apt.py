"""
Look for signs for a pernicious APT (n.b. this plugin is a joke).
"""

def mangle_flow(flow):
    if 'User-Agent: X' in flow['payload']: # OH NO, THE APT HAS PERVERTED THE PACKET!
        flow['apt'] = 'yep'
    else:
        flow['apt'] = 'nah'

    return flow
