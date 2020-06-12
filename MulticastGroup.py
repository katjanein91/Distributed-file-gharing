import socket
import struct
import sys
import json
import threading, time

#IP Multicast group
MULTICAST_GROUP="224.0.0.0"
MULTICAST_SERVER_ADDR = ('', 10000)
group = []

def reset_group():
    global group
    print("reset group view: ", time.ctime())
    group = []
    threading.Timer(5.0, reset_group).start() 

class MulticastGroup:
    def __init__(self):
        #Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Bind to the server address
        self.sock.bind(MULTICAST_SERVER_ADDR)
        #Tell the operating system to add the socket to the multicast group
        #on all interfaces.
        group = socket.inet_aton(MULTICAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        #Set function with timer to reset the group view every X seconds
        reset_group()

    def update_group(self):
        global group
        server_address = ""
        print('\nwaiting to receive message')
        try:
            data, address = self.sock.recvfrom(1024)
            server_address = address[0]

            print('received %s bytes from %s' % (len(data), address))
            print(data)
        
            print('sending acknowledgement to', address)
            self.sock.sendto(b'ack', address)
            #Create group
            if not server_address in group:
                group.append(server_address)
        except:
            pass
        return group
        
