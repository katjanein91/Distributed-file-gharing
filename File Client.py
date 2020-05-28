"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket
from Checksum import Checksum

if __name__ == "__main__":
    
    #Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 3000)
    #Receive buffer size
    buffer_size = 4096

    message = 'file'
    filename = r"C:\Users\Tobi\Desktop\test2.txt"
    cs = Checksum(filename)

    try:
        client_socket.connect(server_address)
        #Send data
        client_socket.sendall(message.encode())
        print('Sent to server: ', message)

        while True:
            # Receive response
            print('Waiting for response...')
            data = client_socket.recv(buffer_size)
            print('Received message from server: ', data.decode())
            
            if data.decode() == 'This is a test':
                f = open(filename, "w")
                f.write(data.decode())
                f.close()
            if "checksum" in data.decode():
                received_checksum = data.decode().split("=")[1]
                checksum = cs.generate_digest()
                if received_checksum == checksum:
                    print("file transmitted without errors")
                else:
                    print("file corrupted while transmitting!!")
                
            if not data:
                break
            
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
        print("Closing socket")
        client_socket.close()
        
    finally:
        client_socket.close()
        print('Socket closed')
