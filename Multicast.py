import socket
import struct
import sys
import signal
import json
import re
import threading, time
import numpy as np
from LCR import LCR
from datetime import datetime

#IP Multicast group
MULTICAST_GROUP="224.0.0.0"
MULTICAST_SERVER_ADDR = ("", 10000)
MSG_SEND_INTERVAL = 5.0
GROUP_UPDATE_INTERVAL = 2.0
COUNTER_CHECK_INTERVAL = 10.0    

#Thread 
class Multicast(object):
    def __init__(self, *args):
            self.group = {}
            self.desired_group_length = 3
            self.server_msg_count={}
            self.vector_clock = [0,0,0]
            self.allowed_to_send = True
            self.leader_selected = False
            self.leader_ip = None
            self.leader_id = 0
            self.sorted_ids = []
            self.start_time = time.time()
            self.current_runtime = 0
            self.args = args
            self.server_id = self.args[0]
            self.server_ip = self.args[1]
            self.multicast_transmit_socket = None
            self.multicast_receive_socket = None
            self.multicast_message = ""
            signal.signal(signal.SIGINT,self.signal_handling) 
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True                            # Daemonize thread
            thread.start()                                  # Start the execution

    #Ctrl + C handling
    def signal_handling(self,signum,frame):           
        print("caught keyboard interrupt, exiting")
        sys.exit(1)

    def create_udp_transmit_socket(self):
        try:
            print('Create UDP socket')
            self.multicast_transmit_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.multicast_transmit_socket.settimeout(10.0)
            #Set the time-to-live for messages to 1 so they do not go past the
            #local network segment.
            ttl = struct.pack('b', 32)
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
            host = self.server_ip
            self.multicast_receive_socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
            self.multicast_receive_socket.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, 
                            socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton(host))
        except socket.error:
            print("Error creating udp receive socket")

    def check_counter(self):
        #self.group = {}
        if (len(self.server_msg_count) > 0):
            #print("Check msg counter")
            for key in self.server_msg_count.keys():
                counter = self.server_msg_count.get(key)
                #Reset the counter after the check time interval
                if (counter > 0):
                    self.server_msg_count[key] = 0
                #Server sent no messages within the check time interval
                elif (counter == 0):
                    del self.server_msg_count[key]
                    del self.group[key]
                    self.vector_clock[key - 1] = 0
                    print('remove server %d from list' % (key))
                    break

        #Start Thread every X seconds
        threading.Timer(COUNTER_CHECK_INTERVAL, self.check_counter).start() 

    def update_group(self):
        server_address = ""
        try:
            data, address = self.multicast_receive_socket.recvfrom(1024)
            now = time.time()
            self.current_runtime = int(now % 60) - int(self.start_time % 60)
            #print("current runtime: ", self.current_runtime)
            server_address = address[0]

            if "Server ID" in data.decode():
                id_str=data.decode().split("Server ID",1)[1] 
                server_id=[int(s) for s in re.findall(r'\b\d+\b', id_str)][0]

                if (server_id in self.server_msg_count):
                    self.server_msg_count[server_id] = self.server_msg_count[server_id] + 1
                else:
                    self.server_msg_count[server_id] = 1

                if "vc" in data.decode():
                    received_vector_clock = data.decode().split("vc=",1)[1]
                    received_vector_clock = [int(s) for s in re.findall(r'\b\d+\b', received_vector_clock)]

                    #print('received message from Process {}. Vector Clock is {}'.format(server_id, received_vector_clock))
                    for id in range(len(self.vector_clock)):
                        self.vector_clock[id-1] = max(received_vector_clock[id-1], self.vector_clock[id-1])

                if not server_address in self.group.values():
                    self.group[server_id]=server_address

            if "LEADER" in data.decode():
                self.leader_ip = server_address
                self.leader_selected = True
                
            print('received "%s" from server %s' % (data, address))  
            #print('sending acknowledgement to', address)
            #self.multicast_socket.sendto(b'ack', address)

            #All 3 nodes has to be up within 10 seconds 
            #Start leader election
            if (len(self.group) >= self.desired_group_length) and (self.current_runtime > 10) and self.leader_selected == False:
                server_ids=list(self.group.keys())
                self.sorted_ids = sorted(server_ids)
                self.server_msg_count=dict.fromkeys(self.sorted_ids, 0)
                #avoid -1 index out of range
                lcr = LCR(self.sorted_ids[0])
                nodes = [lcr]
                for i in range(1, len(self.sorted_ids)):
                    node = LCR(self.sorted_ids[i])
                    #Tell the current node in nodes array the right neighbour 
                    nodes[-1].next_node = node
                    nodes.append(node)
                #Tell the last node in nodes array the right neighbour 
                nodes[-1].next_node = nodes[0]
                #First node starts election
                nodes[0].start_election()
                self.leader_id = lcr.leader
                self.leader_selected = True

            elif ((len(self.group) < self.desired_group_length) and (self.current_runtime > 10) and (self.leader_selected == False)):
                if (len(self.group) < 2):
                    self.desired_group_length = 1
                elif (len(self.group) < 3):
                    self.desired_group_length = 2
                else:
                    self.desired_group_length = 3

            #If a node goes down and a leader is selected, start a new election
            if (len(self.group) < self.desired_group_length) and self.leader_selected == True:
                self.leader_selected = False
                if (len(self.group) < 2):
                    self.desired_group_length = 1
                elif (len(self.group) < 3):
                    self.desired_group_length = 2
                else:
                    self.desired_group_length = 3

        except socket.timeout:
            print("timeout receiving over udp socket")
            pass
            
        #Start Thread every X seconds
        threading.Timer(GROUP_UPDATE_INTERVAL, self.update_group).start()  

    def send_message(self):
        print("Group view: ", self.group)

        masked_vc = np.ma.masked_equal(self.vector_clock, 0, copy=False)
        min_vc = masked_vc.min()
        if (len(self.group) > 1 and ((self.vector_clock.index(min_vc) + 1) == int(self.server_id))):
            print("Allowed to send")
            self.allowed_to_send = True
        else:
            now = time.time()
            if ((int(now % 60) > (int(self.start_time % 60) + 20)) and self.desired_group_length > 1):
                self.allowed_to_send = False

        if (self.allowed_to_send == True):
            #Increase vector clock
            self.vector_clock[int(self.server_id)-1] += 1
            if (self.leader_id == int(self.server_id) or self.desired_group_length == 1):
                self.multicast_message =  b'LEADER Server ID ' + bytes(self.server_id, 'utf-8') + b' vc=' + bytes(str(self.vector_clock), 'utf-8')
            else:
                self.multicast_message =  b'Server ID ' + bytes(self.server_id, 'utf-8') + b' vc=' + bytes(str(self.vector_clock), 'utf-8')

            #Send data to the multicast group
            print("Send message to multicast group: ", self.multicast_message)
            self.multicast_transmit_socket.sendto(self.multicast_message, (MULTICAST_GROUP, 10000))

        #Start Thread every X seconds
        threading.Timer(MSG_SEND_INTERVAL, self.send_message).start() 

    def run(self):
        self.create_udp_transmit_socket()
        self.create_udp_receive_socket()

        self.send_message()
        #Update the group view
        self.update_group()
        #Set function with timer to check msg counter every X seconds
        self.check_counter()
   




        
