from flask import Flask, render_template
import socket
from scapy.all import sniff

app = Flask(__name__)
sniffed_ips = []  # List to store sniffed IPs

def packet_callback(packet):
    if packet.haslayer('IP'):
        ip_src = packet['IP'].src
        ip_dst = packet['IP'].dst
        target_ip = '192.168.139.43'  # Replace with the IP address you want to sniff
        if ip_src == target_ip or ip_dst == target_ip:
            print(f"IP Source: {ip_src} --> IP Destination: {ip_dst}")
            sniffed_ips.append(f"IP Source: {ip_src} --> IP Destination: {ip_dst}")
@app.route('/')
def index():
    return render_template('index.html', sniffed_ips=sniffed_ips)

@app.route('/receive-image', methods=['POST'])
def receive_image():
    host = '0.0.0.0'  # Use '0.0.0.0' to listen on all available interfaces
    port = 12345  # Use the same port number used by the server

    # Create a socket to listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)  # Listen for one incoming connection

    print(f"Waiting for connection on port {port}...")
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    # Receive and save the image
    received_image = b''  # Initialize an empty byte string to store the image data
    while True:
        image_chunk = client_socket.recv(4096)  # Receive 4KB chunks of the image data
        if not image_chunk:
            break
        received_image += image_chunk

    # Save the received image to a file
    with open('static/received_image.jpg', 'wb') as file:  # Save to 'static' folder
        file.write(received_image)

    print("Image received and saved as 'received_image.jpg'")

    # Close the sockets
    client_socket.close()
    server_socket.close()
    return "Image received and saved successfully"

@app.route('/start-sniffing', methods=['POST'])
def start_sniffing():
    network_interface = 'Wi-Fi'  # Replace with your network interface
    print(f"Starting packet sniffing on interface {network_interface}...")

    # Start the packet sniffing process
    sniff(iface=network_interface, prn=packet_callback, store=0)

    return "Packet sniffing started"

if __name__ == "__main__":
    app.run(debug=True)