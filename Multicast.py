import socket
import struct
import sys
import json
import threading, time
from Ring import Ring
from LCR import LCR
from datetime import datetime

#IP Multicast group
MULTICAST_GROUP="224.0.0.0"
MULTICAST_SERVER_ADDR = ('', 10000)

#Thread 
class Multicast(object):
    def __init__(self, *args):
            #Create UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #Bind to the server address
            self.sock.bind(MULTICAST_SERVER_ADDR)
            #Tell the operating system to add the socket to the multicast group
            #on all interfaces.
            group = socket.inet_aton(MULTICAST_GROUP)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.group = []
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            #Set function with timer to reset the group view every X seconds
            self.reset_group()
            self.leader_selected = False
            self.leader_ip = None
            self.start_time = datetime.now()
            self.current_runtime = 0
            self.args = args
            thread = threading.Thread(target=self.run, args=(self.args[0],self.args[1]))
            thread.daemon = True                            # Daemonize thread
            thread.start()                                  # Start the execution

    def create_udp_socket(self):
        try: 
            #Create a UDP socket
            print('Create UDP socket')
            multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            multicast_socket.settimeout(5.0)
            #Set the time-to-live for messages to 1 so they do not go past the
            #local network segment.
            ttl = struct.pack('b', 1)
            multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            return multicast_socket
        except socket.error:
            print("Error creating udp socket")

    def reset_group(self):
        print("reset group view: ", time.ctime())
        self.group = []
        threading.Timer(10.0, self.reset_group).start() 

    def update_group(self, server):
        server_address = ""
        print('\nwaiting to receive message')
        try:
            data, address = self.sock.recvfrom(1024)
            time = datetime.now()
            self.current_runtime = time - self.start_time
            server_address = address[0]

            print('received %s bytes from %s' % (len(data), address))
            print(data)
        
            print('sending acknowledgement to', address)
            self.sock.sendto(b'ack', address)
            #Create group
            if not server_address in self.group:
                self.group.append(server_address)

            #Start leader election
            #if (len(self.group) > 1) and self.leader_selected == False:
            if (len(self.group) == 1) and self.leader_selected == False:
                #ring = Ring(self.group)
                #sorted_ips = ring.form_ring()
                count = len(self.group)
                nodes = [LCR(None, self.group)]
                for _ in range(count - 1):
                    node = LCR(None, self.group)
                    nodes[-1].next_node = node
                    nodes.append(node)
                nodes[-1].next_node = nodes[0]

                nodes[0].start_election()
                if nodes[0].leader != False:
                    self.leader_selected = True
                    if nodes[0].leader == server[1]:
                        self.leader_ip = server[1]
                        print("Leader IP is: " + self.leader_ip)

            #All 3 nodes has to be up within 10 seconds 
            #If a node goes down and a leader is selected, start a new election
            if (len(self.group) < 3) and (self.current_runtime.seconds > 10) and self.leader_selected == True:
                print("Starting new leader election...")
                self.leader_selected = False
        except:
            pass
        return self.group

    def run(self, server_id, server_ip):
        server = [server_id, server_ip]
        multicast_socket = self.create_udp_socket()
        try:
            while True:
                #Send data to the multicast group
                multicast_message = b'Server ' + bytes(server_id, 'utf-8')
                print("Send message to multicast group: ", multicast_message)
                multicast_socket.sendto(multicast_message, (MULTICAST_GROUP, 10000))
                time.sleep(5)
                #Update the group view
                group_view = self.update_group(server)
                print(group_view)
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")




        
