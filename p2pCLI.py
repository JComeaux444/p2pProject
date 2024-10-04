import socket
import sys


def handle_help():
    print("\nHelp Menu:")
    print("1. Help - Shows this help message.")
    print("2. myip - Shows the current users IP.")
    print("3. myport - Displays current port listening on.")
    print("4. connect - Allows you to connect to another client on the LAN, <destination> is the IP, <port no> is their port number.")
    print("5. list - Shows the current IPs and ports you are connected to and their id number.")
    print("6. terminate - Using the command with arg <connection id.> will disconnect that client from your socket")
    print("7. send - Uses first arg <connection id.> found in list to send the second arg <message> to that client/IP.")
    print("8. Exit - Exits the program.")


# List of known connections we can talk to
knownConnections = [["IP 127.420.690.11", "4545"]]

def handle_list():
    
    print("\nList of connections:")
    print("id:    IP address     Port No.")
    for i in range(len(knownConnections)):
        print(i,'   ',knownConnections[i])


def get_my_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"My IP Address: {ip_address}")


class Client:
    def __init__(self, host, port):
        self.server = None
        self.port = port
        self.host = host
        self.inputs = []
        self.connection_list = {}
        self.id_counter = 1
        self.running = True
    
    while True:
    
        
        choice = input("\nEnter your choice (number or text): ").strip().lower()

        if choice in ['help']:
            handle_help()
        elif choice in ['myip']:
            get_my_ip()
        elif choice in ['myport']:
            continue
        elif choice in ['connect']:
            # We will parse the rest in here
            continue   
        elif choice in ['list']:
            handle_list()
        elif choice in ['terminate']:
            # find what connection to term
            continue
        elif choice in ['send']:
            # parse here too
            continue
        elif choice in ['exit']:
            print("\nExiting the program...")
            break
        else:
            print("\nChoice is Invalid! Please use the whole word with correct args.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please start the program using \'chat.py <port number>\' use 4545 or any other port number")
        sys.exit(1)

    port = int(sys.argv[1])
    host = socket.gethostbyname(socket.gethostname())
    peer = Client(host, port)
    handle_help()
    peer.start_server()
