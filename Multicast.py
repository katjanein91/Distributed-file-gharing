import socket
import struct
import sys
import json
import threading, time
from LCR import LCR
from datetime import datetime

#IP Multicast group
MULTICAST_GROUP="224.0.0.0"
MULTICAST_SERVER_ADDR = ("", 10000)

#Thread 
class Multicast(object):
    def __init__(self, *args):
            self.group = {}
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
        except socket.error:
            print("Error creating udp receive socket")

    def reset_group(self):
        if (len(self.group) != 3):
            print("reset group view: ", time.ctime())
            self.group = {}
            threading.Timer(10.0, self.reset_group).start() 

    def update_group(self):
        server_address = ""
        print('\nwaiting to receive message')
        try:
            data, address = self.multicast_receive_socket.recvfrom(1024)
            server_id=0
            time = datetime.now()
            self.current_runtime = time - self.start_time
            server_address = address[0]

            if "Server ID" in data.decode():
                server_id=int(data.decode().split("Server ID",1)[1].strip())
                
            print('received "%s" from server %s %s' % (data, address, server_id))  
            #print('sending acknowledgement to', address)
            #self.multicast_socket.sendto(b'ack', address)
            #Create group
            if not server_address in self.group:
                self.group[server_id]=server_address

            #Start leader election
            if (len(self.group) > 1) and self.leader_selected == False:
            #if (len(self.group) == 1) and self.leader_selected == False:
                server_ids=list(self.group.keys())
                sorted_ids = sorted(server_ids)
    
                count = len(sorted_ids)
                nodes = [LCR(None, sorted_ids)]
                for _ in range(count - 1):
                    node = LCR(None, sorted_ids)
                    nodes[-1].next_node = node
                    nodes.append(node)
                nodes[-1].next_node = nodes[0]

                nodes[0].start_election()
                if nodes[0].leader != False:
                    self.leader_selected = True
            
            if (len(self.group) == 1) and self.leader_selected == False:
                self.leader_ip = self.server_ip
                print("Leader IP is: " + self.leader_ip)

            #All 3 nodes has to be up within 10 seconds 
            #If a node goes down and a leader is selected, start a new election
            if (len(self.group) < 3) and (self.current_runtime.seconds > 10) and self.leader_selected == True:
                print("Starting new leader election...")
                self.leader_selected = False
        except socket.timeout:
            print("timeout receiving over udp socket")
            pass
        print(self.group)
        threading.Timer(5.0, self.update_group).start()  

    def send_message(self):
        if (self.leader_ip == self.server_ip):
            self.multicast_message =  b'LEADER Server ID ' + bytes(self.args[0], 'utf-8')
        else:
            self.multicast_message =  b'Server ID ' + bytes(self.args[0], 'utf-8')

        #Send data to the multicast group
        print("Send message to multicast group: ", self.multicast_message)
        self.multicast_transmit_socket.sendto(self.multicast_message, (MULTICAST_GROUP, 10000))
        threading.Timer(10.0, self.send_message).start() 

    def run(self):
        self.create_udp_transmit_socket()
        self.create_udp_receive_socket()
        try:
            self.send_message()
            #Update the group view
            self.update_group()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")




        
