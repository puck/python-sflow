"""
Bravely dispatch the flow's payload to scapy to dissect. Collect up just some dissected properties.
"""

import logging
import pdb
import sys

logging.getLogger("scapy").setLevel(1)
from scapy.all import *

class ForkedPdb(pdb.Pdb):
    """
    A Pdb subclass that may be used from a forked multiprocessing child.

    Borrowed from <http://stackoverflow.com/a/23654936> for debugging.
    """

    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = file('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin

def mangle_flow(flow):
    dissected = Ether(flow['payload'])

    # only bother with some properties for this demo...

    if 'TCP' in dissected:
        flow['metadata']['sport'] = dissected['TCP'].sport
        flow['metadata']['dport'] = dissected['TCP'].dport
        flow['metadata']['flags'] = dissected['TCP'].sprintf('%TCP.flags%')
        flow['metadata']['transport'] = 'TCP'

    if 'UDP' in dissected:
        flow['metadata']['sport'] = dissected['UDP'].sport
        flow['metadata']['dport'] = dissected['UDP'].dport
        flow['metadata']['transport'] = 'UDP'        

    return flow
