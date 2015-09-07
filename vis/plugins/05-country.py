"""
Determine the country of a flow.
"""

import GeoIP

gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)

def mangle_flow(flow):
    if flow['metadata']['has_ip'] == False:
        return flow

    country = gi.country_code_by_addr(flow['metadata']['remote_address'])
    if country is not None:
        flow['metadata']['country'] = country

    return flow
