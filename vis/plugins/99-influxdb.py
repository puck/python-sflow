"""
Send packets to magical InfluxDB!
"""

from influxdb import InfluxDBClient

influx_client = InfluxDBClient('localhost', 8086, 'root', 'root', 'sflow')

def mangle_flow(flow):

    json_body = [
        {
            "measurement": "realtime",
            "tags": flow['metadata'],
            "fields": {
                "packets": flow['sample']['sampling_rate'],
                "octets": (flow['frame_length'] - flow['stripped'] - flow['header_length']) * flow['sample']['sampling_rate'],
            }
        }
    ]

    influx_client.write_points(json_body)

    return flow
