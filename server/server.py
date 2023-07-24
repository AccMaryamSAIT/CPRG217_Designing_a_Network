
import socket, time, hashlib, os, tqdm

client_ip = '0.0.0.0' # 0.0.0.0 means that server accepts connection from any IP. Otherwise, we can specify a specific address.
server_port = 5000
buffer_size = 1024
sep = '}}'

server_socket = socket.socket() # Or use with socket.socket(variables) as s
server_socket.bind((client_ip, server_port)) # Make server remember this connection
server_socket.listen(5) # Keep out for any messages. Int value defines how many parallel connections does the server allow. aka how many PCs connect at the same time.
print(f'Listening for message on {server_port} from {client_ip}...') # If the connection was made this will print. Otherwise an error prints instead. The program cannot move on until the connection is made.

client_socket, client_ip = server_socket.accept() # allows us to accept the connection
print(f'Accepted connection from {client_ip}.')

# use client socket for everything here after we accepted the connection
msg = client_socket.recv(buffer_size).decode() # use buffer size in recv(). Also, decode the message. MESSAGE is recieved from client socket not server socket.
filename, EOF, hashRecieved, filesize = msg.split(sep)
print(f'Filename: {filename}\nEnd of File: {EOF}\nHash: {hashRecieved}.')

time.sleep(2)
reply = 'OK'.encode() # Encoding to convert to binary in order to be able to send it.
client_socket.sendall(reply) # Better to use if you want to send everything. 

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
server_socket.close() # close connection after job is done to close port and prevent security vulnerabilities. Connection and port are no longer needed.
client_socket.close()
# good practice to close manually but can occur automatically. 

