from uuid import uuid4

ELECTION = 0
NEW_LEAD = 1

class LCR:
    def __init__(self, node):
        self.next_node = node
        self.uuid = uuid4()
        self.is_participant = False
        self.is_leader = False
        self.leader = False
        
    def start_election(self):
        print("{} is starting an election.".format(self.uuid))
        self.is_participant = True
        self.forward((ELECTION, self.uuid))
        

    def forward(self, message):
        self.next_node.accept(message)

    def accept(self, message):
        group, uuid = message
        if group == ELECTION:
            if uuid > self.uuid:
                print("{} is forwarding without updates.".format(self.uuid))
                self.is_participant = True
                self.forward((ELECTION, uuid))
            if uuid < self.uuid:
                print("{} is updating and forwarding.".format(self.uuid))
                self.is_participant = True
                self.forward((ELECTION, self.uuid))
            if uuid == self.uuid:
                print("{} starts acting as a leader!".format(self.uuid))
                self.is_participant = False
                self.is_leader = True
                self.leader = self.uuid
                self.forward((NEW_LEAD, self.uuid))
        if group == NEW_LEAD:
            if uuid == self.uuid:
                return
            if uuid != self.uuid:
                print("{} acknowledged new leader.".format(self.uuid))
                self.leader = uuid
                self.forward((NEW_LEAD, uuid))

