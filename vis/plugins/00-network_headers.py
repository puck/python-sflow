"""
Digest the network headers (L2 and partial L3) for a particular flow.
"""

import frame

def mangle_flow(flow):
    decoded_frame = frame.Frame(flow['payload'])
    flow['metadata'].update(decoded_frame.to_dict())
    flow['header_length'] = decoded_frame.sum_header_lengths()
    return flow
