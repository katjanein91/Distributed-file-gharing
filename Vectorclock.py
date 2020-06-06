# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from multiprocessing import Process, Pipe
from time import sleep

class Vecltorcl:

    def event(pid, counter):
        counter[pid-1] += 1
        print('Process {} performed local event. Vector Clock is {}'.format(pid, counter))
        return counter
    
    def send_message(pipe, pid, counter):
        counter[pid-1] += 1
        pipe.send((pid, counter))
        print('Process {} sent message. Vector Clock is {}'.format(pid, counter))
        return counter
    

    def recv_message(pipe, pid, counter):
        sender_id, ts = pipe.recv()
        counter[pid-1] += 1
        for id in range(len(counter)):
            counter[id-1] = max(ts[id-1], counter[id-1])
        print('Process {} received message from Process {}. Vector Clock is {}'.format(pid, sender_id, counter))
        return counter

    def process_one(pipe12):
        pid = 1
        counter = [0,0,0]
        counter = event(pid, counter)
        counter = send_message(pipe12, pid, counter)
        sleep(3)
        counter  = event(pid, counter)
        counter = recv_message(pipe12, pid, counter)
        counter  = event(pid, counter)
    
    def process_two(pipe21, pipe23):
        pid = 2
        counter = [0,0,0]
        counter = recv_message(pipe21, pid, counter)
        counter = send_message(pipe21, pid, counter)
        counter = send_message(pipe23, pid, counter)
        counter = recv_message(pipe23, pid, counter)


    def process_three(pipe32):
        pid = 3
        counter = [0,0,0]
        counter = recv_message(pipe32, pid, counter)
        counter = send_message(pipe32, pid, counter)
        
    if __name__ == '__main__':
        one_two, two_one = Pipe()
        two_three, three_two = Pipe()

        process1 = Process(target=process_one, args=(one_two,))
        process2 = Process(target=process_two, args=(two_one, two_three))
        process3 = Process(target=process_three, args=(three_two,))

    process1.start()
    process2.start()
    process3.start()

    process1.join()
    process2.join()
    process3.join()

