"""
Look for signs for a pernicious APT (n.b. this plugin is a joke).
"""

import re

apt_finder = re.compile('X-Dissident-ID: (\d+)')

def mangle_flow(flow):

    apts = apt_finder.findall(flow['payload'])
    print apts
    
    return flow
