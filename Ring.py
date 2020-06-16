import socket

class Ring:
    def __init__(self, group):
        self.members = group

    def form_ring(self):
        sorted_binary_ring = sorted([socket.inet_aton(member) for member in self.members])
        sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
        print("Sorted group: "+ sorted_ip_ring)
        return sorted_ip_ring


    def get_neighbour(self, current_member_ip, direction='left'):
        members = self.members
        current_member_index = members.index(current_member_ip) if current_member_ip in members else -1
        if current_member_index != -1:
            if direction == 'left':
                if current_member_index + 1 == len(members):
                    return members[0]
                else:
                    return members[current_member_index + 1]
            else:
                if current_member_index - 1 == 0:
                    return members[len(members) - 1]
                else:
                    return members[current_member_index - 1]
        else:
            return None

