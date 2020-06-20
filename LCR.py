from uuid import uuid4

ELECTION = 0
NEW_LEAD = 1

class LCR:
    def __init__(self, node, server_group):
        self.next_node = node
        self.server_id = int(server_group[0])
        self.is_participant = False
        self.is_leader = False
        self.leader = False
        
    def start_election(self):
        print("Server {} is starting an election.".format(self.server_id))
        self.is_participant = True
        self.forward((ELECTION, self.server_id))
        
    def forward(self, message):
        self.next_node.accept(message)

    def accept(self, message):
        group, uuid = message
        if group == ELECTION:
            if uuid > self.server_id:
                print("Server {} is forwarding without updates.".format(self.server_id))
                self.is_participant = True
                self.forward((ELECTION, uuid))
            if uuid < self.server_id:
                print("Server {} is updating and forwarding.".format(self.server_id))
                self.is_participant = True
                self.forward((ELECTION, self.server_id))
            if uuid == self.server_id:
                print("Server {} starts acting as a leader!".format(self.server_id))
                self.is_participant = False
                self.is_leader = True
                self.leader = self.server_id
                self.forward((NEW_LEAD, self.server_id))
        if group == NEW_LEAD:
            if uuid == self.server_id:
                return
            if uuid != self.server_id:
                print("Server {} acknowledged new leader.".format(self.server_id))
                self.leader = uuid
                self.forward((NEW_LEAD, uuid))

