import socket, hashlib, time, tqdm, os

#cronjob and crontab
#cron is a linux daemon drived from greek which means time
#crond is used to run specific tasks on linux within specified time frames
#5* command (***** command)
#each star has a meaning:
#1st = minute (0-59mins)
#2nd = hour (0-23)
#3rd = day of month (1-31)
#4th = month (1-12)
#5th = day of the week (sunday to saturday --> 0-6 (7 is sunday again))
#leave stars if not using the values (e.g. every 15 minutes looks like 15 * * * *)
#use commas between values if e.g. (every 15 and 45 minutes looks like 15,45 * * * *)
#use dashes between values if e.g. (between 30-45 minutes looks like 30-45 * * * *)
#command = e.g. (python3 /fullpath/filename) <-- wanting to run python file

server_ip = '127.0.0.1'
server_port = 5000
buffer_size = 1024
EOF = ':EOF:'
sep = '}}'

filename = input('Please enter filename: ')
print(filename)
filesize = os.stat(filename)
filesize = filesize.st_size

with open(filename, 'rb') as f:
    hash = hashlib.md5(f.read()).hexdigest()
    print(f'File hash is: {hash}')

client_socket = socket.socket() # Or use with socket.socket(variables) as s
client_socket.connect((server_ip, server_port)) # Send it as a tuple
print('Connected to server.') # If the connection was made this will print. Otherwise an error prints instead. The program cannot move on until the connection is made.

msg = filename+sep+EOF+sep+hash+sep+str(filesize) # Encoding to convert to binary in order to be able to send it.
progress = tqdm.tqdm(range(filesize), f'Sending file {filename}', unit='B', unit_scale=True, unit_divisor=1024)

client_socket.sendall(msg.encode()) # Better to use if you want to send everything. 
reply = client_socket.recv(buffer_size).decode() # use buffer size in recv(). Also, decode the message

if reply == 'OK':
    with open(filename, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                progress.close()
                time.sleep(1)
                client_socket.sendall(EOF.encode())
                break
            else:
                client_socket.sendall(data)
                progress.update(len(data))

print('File sent successfully. Awaiting confirmation.')

reply = client_socket.recv(buffer_size).decode()
if reply == 'SUCCESS':
    print('Transfer complete.')
elif reply == 'ERROR_CHECKSUM':
    print('Checksum error. File corrupted during transfer.')
else:
    print(f'Unkown message recieved: {reply}')

client_socket.close() # close connection after job is done to close port and prevent security vulnerabilities. Connection and port are no longer needed.
# good practice to close manually but can occur automatically. 

