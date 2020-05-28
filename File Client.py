"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket

if __name__ == "__main__":
    
    #Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 3000)
    #Receive buffer size
    buffer_size = 4096

    message = 'file'
    filename = r"C:\Users\Tobi\Desktop\test2.txt"

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
                break
            if not data:
                break
            
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
        print("Closing socket")
        client_socket.close()
        
    finally:
        client_socket.close()
        print('Socket closed')
