import socket
import struct
import sys
import numpy as np

#IP Multicast group
MULTICAST_GROUP="224.0.0.0"
MULTICAST_SERVER_ADDR = ('', 10000)

class MulticastGroup:
    def __init__(self):
        self.group = []
        self.server_addresses = []
        #Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Bind to the server address
        self.sock.bind(MULTICAST_SERVER_ADDR)
        #Tell the operating system to add the socket to the multicast group
        #on all interfaces.
        group = socket.inet_aton(MULTICAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    def update_group(self):
        print('\nwaiting to receive message')
        data, address = self.sock.recvfrom(1024)
        server_address = address[0]
        if not server_address in self.server_addresses:
            self.server_addresses.append(server_address)

        print('received %s bytes from %s' % (len(data), address))
        print(data)
    
        print('sending acknowledgement to', address)
        self.sock.sendto(b'ack', address)

        #Create group
        self.group = self.server_addresses

        self.server_addresses = []
        return self.group
        
