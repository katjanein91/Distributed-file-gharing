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
MULTICAST_SERVER_ADDR = ("", 10000)

#Thread 
class Multicast(object):
    def __init__(self, *args):
            self.group = []
            #Set function with timer to reset the group view every X seconds
            self.reset_group()
            self.leader_selected = False
            self.leader_ip = None
            self.start_time = datetime.now()
            self.current_runtime = 0
            self.args = args
            self.server_id = self.args[0]
            self.server_ip = self.args[1]
            self.multicast_transmit_socket = None
            self.multicast_receive_socket = None
            self.multicast_message = ""
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True                            # Daemonize thread
            thread.start()                                  # Start the execution

    def create_udp_transmit_socket(self):
        try:
            print('Create UDP socket')
            self.multicast_transmit_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.multicast_transmit_socket.settimeout(10.0)
            #Set the time-to-live for messages to 1 so they do not go past the
            #local network segment.
            ttl = struct.pack('b', 1)
            self.multicast_transmit_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    
        except socket.error:
            print("Error creating udp transmit socket")

    def create_udp_receive_socket(self):
        try:
            self.multicast_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.multicast_receive_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
            self.multicast_receive_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
            #allow reuse of socket (to allow another instance of python running this
            #script binding to the same ip/port)
            self.multicast_receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #Bind to the server address
            self.multicast_receive_socket.bind(MULTICAST_SERVER_ADDR)
            host = socket.gethostbyname(socket.gethostname())
            self.multicast_receive_socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
            self.multicast_receive_socket.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, 
                            socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton(host))
            #Tell the operating system to add the socket to the multicast group
            #on all interfaces.
            # group = socket.inet_aton(MULTICAST_GROUP)
            # mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            # self.multicast_receive_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except socket.error:
            print("Error creating udp receive socket")

    def reset_group(self):
        print("reset group view: ", time.ctime())
        self.group = []
        threading.Timer(10.0, self.reset_group).start() 

    def update_group(self, server):
        server_address = ""
        print('\nwaiting to receive message')
        try:
            data, address = self.multicast_receive_socket.recvfrom(16)
            time = datetime.now()
            self.current_runtime = time - self.start_time
            server_address = address[0]

            print('received "%s" from %s' % (data, address))  
            #print('sending acknowledgement to', address)
            #self.multicast_socket.sendto(b'ack', address)
            #Create group
            if not server_address in self.group:
                self.group.append(server_address)

            #Start leader election
            if (len(self.group) > 1) and self.leader_selected == False:
            #if (len(self.group) == 1) and self.leader_selected == False:
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
        except socket.timeout:
            print("timeout receiving over udp socket")
            pass
        return self.group

    def send_message(self):
        if (self.leader_ip == self.server_ip):
            self.multicast_message =  b'LEADER Server ' + bytes(self.args[0], 'utf-8')
        else:
            self.multicast_message =  b'Server ' + bytes(self.args[0], 'utf-8')

        #Send data to the multicast group
        print("Send message to multicast group: ", self.multicast_message)
        self.multicast_transmit_socket.sendto(self.multicast_message, (MULTICAST_GROUP, 10000))

    def run(self):
        server = [self.server_id, self.server_ip]
        self.create_udp_transmit_socket()
        self.create_udp_receive_socket()
        try:
            while True:
                self.send_message()
                #Update the group view
                group_view = self.update_group(server)
                print(group_view)
                time.sleep(5)
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")




        
