import binascii
import ipaddr
import socket
import struct

class Frame(object):
    """
    Given the raw bytes of an Ethernet II frame extract some useful parameters.
    """

    ETHERTYPES = {
        'IPv4': 0x0800,
        '802.1Q': 0x8100,
        'IPv6': 0x86DD,
    }

    HEADER_LENGTHS = {
        'Ether': 14, # octets
        'Dot1Q': 4, # octets
    }

    def __init__(self, packet):
        if len(packet) < 14: # packet is too short to have an Ethernet header...
            raise Exception("Packet too short (under 14 octets)")

        # decode ethernet frame header
        self.ethernet_header = struct.unpack("!6s6sH", packet[0:14])
        self.destination_mac = binascii.hexlify(self.ethernet_header[0])
        self.source_mac = binascii.hexlify(self.ethernet_header[1])
        self.ethertype = self.ethernet_header[2]

        # find all 802.1q headers, if any
        if self.ethertype == self.ETHERTYPES['802.1Q']:
            self.vlans = []
            while True:
                self.payload_offset = 12 + len(self.vlans) * 4
                tpid, tci = struct.unpack("!HH", packet[self.payload_offset:self.payload_offset+4])
                if tpid == self.ETHERTYPES['802.1Q']:
                    self.vlans.append(tci & 0x0fff)
                else:
                    self.ethertype = tpid
                    break
        else:
            self.payload_offset = 14

        # decode some of the IPv4 and IPv6 fields important for accting
        if self.ethertype == self.ETHERTYPES['IPv4']:
            self.ipv4_header = struct.unpack("!BBHHHBBH4s4s", packet[self.payload_offset:self.payload_offset+20])
            self.ipv4_total_length = self.ipv4_header[2]
            self.ipv4_protocol = self.ipv4_header[6]
            self.ipv4_source_ip = socket.inet_ntoa(self.ipv4_header[8])
            self.ipv4_destination_ip = socket.inet_ntoa(self.ipv4_header[9])

            self.has_ip = True
            self.ip_version = 4
            self.total_length = self.ipv4_total_length
            self.source_ip = ipaddr.IPAddress(self.ipv4_source_ip)
            self.destination_ip = ipaddr.IPAddress(self.ipv4_destination_ip)

        elif self.ethertype == self.ETHERTYPES['IPv6']:
            self.ipv6_header = struct.unpack("!4sHBB16s16s", packet[self.payload_offset:self.payload_offset+40])
            self.ipv6_source_ip = socket.inet_ntop(socket.AF_INET6, self.ipv6_header[4])
            self.ipv6_destination_ip = socket.inet_ntop(socket.AF_INET6, self.ipv6_header[5])
            self.ipv6_payload_length = self.ipv6_header[1]
            self.ipv6_next_header = self.ipv6_header[2]

            self.has_ip = True
            self.ip_version = 6
            self.total_length = self.ipv6_payload_length + 40
            self.source_ip = ipaddr.IPAddress(self.ipv6_source_ip)
            self.destination_ip = ipaddr.IPAddress(self.ipv6_destination_ip)
        else:
            self.has_ip = False

    def sum_header_lengths(self):
        """
        Return the sum of the octet lengths of the Ethernet and Dot1Q headers.
        """

        return len(getattr(self, 'vlans', [])) * self.HEADER_LENGTHS['Dot1Q'] + self.HEADER_LENGTHS['Ether']

    def to_dict(self):
        desired_keys = (
            'destination_ip',
            'destination_mac',
            'ethertype',
            'has_ip',
            'ip_version',
            'ipv4_destination_ip',
            'ipv4_protocol',
            'ipv4_source_ip',
            'ipv4_total_length',
            'ipv6_destination_ip',
            'ipv6_next_header',
            'ipv6_payload_length',
            'ipv6_source_ip',
            'payload_offset',
            'source_ip',
            'source_mac',
            'total_length',
            'vlans',
        )

        return {k: v for k, v in self.__dict__.items() if k in desired_keys}

    def __repr__(self):
        return '<Frame ethertype=%s has_ip=%s source_address=%s destination_address=%s length=%s>' % (
            self.ETHERTYPES.get(self.ethertype, hex(self.ethertype)),
            repr(self.has_ip),
            self.source_ip,
            self.destination_ip,
            self.total_length,
        )


def mangle_flow(flow):
    frame = Frame(flow['payload'])
    flow['metadata'].update(frame.to_dict())
    flow['metadata']['header_length'] = frame.sum_header_lengths()
    return flow
