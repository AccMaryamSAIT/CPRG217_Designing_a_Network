"""
Name: server.py
Authors: Roman Kapitoulski, Eric Russon, Maryam Bunama
Version: 2.0
Date: July 30, 2023
Description: This script recieves the JSON files sent by the Client.py program on client machines
and stores it. It performs acknowledgement and error-checking throughout the process.
"""

import socket, time, hashlib, os, tqdm

client_ip = '0.0.0.0' # 0.0.0.0 means that server accepts connection from any IP. Otherwise, we can specify a specific address.
server_port = 5000 # The port the script will communicate over.
buffer_size = 1024 # The size of the packet.
sep = '}}' # The data separator. Must be the same as client.py's separator.
 
# Create a socket connection.
server_socket = socket.socket() 
# Make server remember the socket connection.
server_socket.bind((client_ip, server_port)) 
# Listen for a message from the client.
server_socket.listen(5) 
# If the connection was made this will print. Otherwise an error prints in the terminal instead. 
print(f'Listening for message on {server_port} from {client_ip}...') 

# Allow program to accept the connection + print a confirmation
client_socket, client_ip = server_socket.accept() 
print(f'Accepted connection from {client_ip}.')

# Decode the message recieved from the client
msg = client_socket.recv(buffer_size).decode() 
# Assign variables to the information based on the the separator
filename, EOF, hashRecieved, filesize = msg.split(sep)
# Display the information
print(f'Filename: {filename}\nEnd of File: {EOF}\nHash: {hashRecieved}.')

# Wait for 2 seconds
time.sleep(2)
# Send an 'OK' reply to the client after all information was recieved.
reply = 'OK'.encode()
client_socket.sendall(reply)  

# Create progress bar to track the file recieving information from the client.
progress = tqdm.tqdm(range(int(filesize)), f'Sending file {filename}', unit='B', unit_scale=True, unit_divisor=1024)

with open(filename, 'wb') as r:
    while True:
        data = client_socket.recv(buffer_size)
        if data == b':EOF:':
            # If the end of file was recieved, stop the progress bar and continue to the rest of the program
            progress.close()
            break
        else:
            # Recieve data and update progress bar
            r.write(data)
            progress.update(len(data))

# Create a hash from the sent file
hashCreated = hashlib.md5(open(filename, 'rb').read()).hexdigest()

if hashRecieved == hashCreated:
    # Compare the hash sent and the hash created.
    # Print confirmation and send 'SUCCESS' message to client if they match.
    print('File recieved sucessfully and verified')
    client_socket.sendall('SUCCESS'.encode())
else:
    # Print an error, delete the file, and send an 'ERROR_CHECKSUM' to 
    # the server if the hashes don't match. 
    print('Failed to verify checksum.')
    os.remove(filename)
    reply = 'ERROR_CHECKSUM'.encode()
    client_socket.sendall(reply)

# Wait for a second
time.sleep(1)
# Close the client and server connections.
server_socket.close() 
client_socket.close()


