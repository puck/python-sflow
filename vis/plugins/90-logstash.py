"""
Send packets to logstash!
"""

import logging
from logstash_formatter import LogstashFormatterV1

logging.basicConfig(filename='example.log',level=logging.INFO)
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = LogstashFormatterV1()

handler.setFormatter(formatter)
logger.addHandler(handler)

def mangle_flow(flow):

    logger.info("traffic", extra={
      "sflow": flow['metadata'],
      "packets": flow['sample']['sampling_rate'],
      "octets": (flow['frame_length'] - flow['stripped'] - flow['header_length']) * flow['sample']['sampling_rate'],
    })

    return flow
