"""
Name: Server.py
Authors: Roman Kapitoulski, Eric Russon, Maryam Bunama
Version: 1.0
Date: July 25, 2023
Description: This script recieves the JSON files sent by the Client.py program on client machines
and stores it. It performs acknowledgement and error-checking throughout the process.
"""

import socket, time, hashlib, os, tqdm

client_ip = '0.0.0.0' # 0.0.0.0 means that server accepts connection from any IP. Otherwise, we can specify a specific address.
server_port = 5000
buffer_size = 1024
sep = '}}'

server_socket = socket.socket() 
server_socket.bind((client_ip, server_port)) # Make server remember this connection
server_socket.listen(5) # Keep out for any messages.
print(f'Listening for message on {server_port} from {client_ip}...') # If the connection was made this will print. Otherwise an error prints instead. 

client_socket, client_ip = server_socket.accept() # Allow program to accept the connection
print(f'Accepted connection from {client_ip}.')

msg = client_socket.recv(buffer_size).decode() 
filename, EOF, hashRecieved, filesize = msg.split(sep)
print(f'Filename: {filename}\nEnd of File: {EOF}\nHash: {hashRecieved}.')

time.sleep(2)
reply = 'OK'.encode()
client_socket.sendall(reply)  

progress = tqdm.tqdm(range(int(filesize)), f'Sending file {filename}', unit='B', unit_scale=True, unit_divisor=1024)

with open(filename, 'wb') as r:
    while True:
        data = client_socket.recv(buffer_size)
        if data == b':EOF:':
            progress.close()
            break
        else:
            r.write(data)
            progress.update(len(data))

hashCreated = hashlib.md5(open(filename, 'rb').read()).hexdigest()

if hashRecieved == hashCreated:
    print('File recieved sucessfully and verified')
    client_socket.sendall('SUCCESS'.encode())
else:
    print('Failed to verify checksum.')
    os.remove(filename)
    reply = 'ERROR_CHECKSUM'.encode()
    client_socket.sendall(reply)

time.sleep(1)
server_socket.close() 
client_socket.close()


