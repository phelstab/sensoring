import socket

# E4 Streaming Server configuration
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 28000

# Create a socket and connect to the E4 Streaming Server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_ADDRESS, SERVER_PORT))

# Function to send a command to the server
def send_command(command):
    sock.sendall((command + '\r\n').encode())

# Function to receive data from the server
def receive_data():
    return sock.recv(1024).decode('utf-8')

# Get the list of devices connected over BTLE
send_command('device_list')
response = receive_data()
print(response)

# Extract the device ID from the response
device_id = response.split('|')[1].strip().split(' ')[0]

# Connect to the device
send_command(f'device_connect {device_id}')
response = receive_data()
print(response)

# Subscribe to desired data streams
send_command('device_subscribe acc ON')
response = receive_data()
print(response)

send_command('device_subscribe bvp ON')
response = receive_data()
print(response)

send_command('device_subscribe gsr ON')
response = receive_data()
print(response)

# # Continuously receive and process data from the device
# try:
#     while True:
#         data = receive_data().strip()
#         if data:
#             print(data)
# except KeyboardInterrupt:
#     pass

# Disconnect from the device
send_command('device_disconnect')
response = receive_data()
print(response)

# Close the socket connection
sock.close()
