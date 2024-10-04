import socket
import sys
import select
import threading

"""

List of links for docs/ articles that helpped:
https://stackoverflow.com/questions/11591054/python-how-select-select-works
https://docs.python.org/3/howto/sockets.html
https://realpython.com/python-sockets/

"""
def handle_help():
    print("\nHelp Menu:")
    print("1. help - Shows this help message.")
    print("2. myip - Shows the current users IP.")
    print("3. myport - Displays current port listening on.")
    print("4. connect - Allows you to connect to another client on the LAN, <destination> is the IP, <port no> is their port number.")
    print("5. list - Shows the current IPs and ports you are connected to and their id number.")
    print("6. terminate - Using the command with arg <connection id.> will disconnect that client from your socket")
    print("7. send - Uses first arg <connection id.> found in list to send the second arg <message> to that client/IP.")
    print("8. exit - Exits the program.")



class Peer:
    def __init__(self, host, port):
        # server in this context is a socket- We say server because confilcts with socket import
        # Also acts as a server anyways
        self.server = None
        self.port = port
        self.host = host
        # We use inputs for a list of readable sockets we are connected to
        self.inputs = []
        self.connection_list = {}
        # IDs for connection dict. Set at 1 first
        self.id_counter = 1
        self.running = True

    def get_my_ip():
        # Gets name of pc
        hostname = socket.gethostname()
        # Uses name of PC to find the current IP
        ip_address = socket.gethostbyname(hostname)
        print(f"Your IP address is: {ip_address}")

    # PAss in port number so we dont pass in self for no reason
    def get_my_port(port):
        print(f"My Port is: {port}")    


    def start_server(self):
        # Starts the server to accept incoming connections.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # binds (or connects) public host (pc) to the port given
        self.server.bind((self.host, self.port))
        # Listens to incoming connect requests, limited to 5 in it's listening queue before dropping requests
        self.server.listen(5)
        self.inputs.append(self.server)
        print(f"Server started on {self.host}:{self.port}")

        # Start a thread to handle user input separately
        # We need daemon set true so the thread/input doesn't block the packets coming from the socket
        threading.Thread(target=self.handle_user_input, daemon=True).start()

        self.run()

    def run(self):
        """Main loop to handle socket inputs and connections."""
        while self.running:
            readable, _, _ = select.select(self.inputs, [], [])
            for s in readable:
                if s == self.server:
                    client_socket, addr = self.server.accept()
                    self.inputs.append(client_socket)
                    self.connection_list[self.id_counter] = (client_socket, addr)
                    print(f"New connection from {addr[0]}:{addr[1]} assigned ID {self.id_counter}")
                    self.id_counter += 1
                else:
                    data = s.recv(1024)
                    if data:
                        self.handle_received_message(s, data.decode())
                    else:
                        self.remove_connection(s)

    def handle_user_input(self):
        """Handles user input in a separate thread."""
        while True:
            command = input().strip()
            self.handle_command(command)

    def handle_command(self, command):
        """Parses and executes user commands."""
        tokens = command.split()
        if not tokens:
            return
        cmd = tokens[0]

        if cmd == 'help':
            handle_help()
        elif cmd == 'myip':
            self.get_my_ip()
        elif cmd == 'myport':
            self.get_my_port(self.port)
        elif cmd == 'connect':
            if len(tokens) != 3:
                print("Usage: connect <IP> <Port>")
                return
            self.connect_to_peer(tokens[1], int(tokens[2]))
        elif cmd == 'list':
            self.list_connections()
        elif cmd == 'terminate':
            if len(tokens) != 2:
                print("Usage: terminate <ID>")
                return
            self.terminate_connection(int(tokens[1]))
        elif cmd == 'send':
            if len(tokens) < 3:
                print("Usage: send <ID> <Message>")
                return
            self.send_message(int(tokens[1]), ' '.join(tokens[2:]))
        elif cmd == 'exit':
            self.exit()
        else:
            print("Invalid command. Type 'help' for a list of commands.")

    def connect_to_peer(self, ip, port):
        """Establishes a connection to a peer."""
        try:
            for conn in self.connection_list.values():
                if conn[1][0] == ip and conn[1][1] == port:
                    print("Already connected to this peer.")
                    return
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))
            self.inputs.append(client_socket)
            self.connection_list[self.id_counter] = (client_socket, (ip, port))
            print(f"Connected to {ip}:{port} assigned ID {self.id_counter}")
            self.id_counter += 1
        except Exception as e:
            print(f"Failed to connect to {ip}:{port}. Error: {e}")

    def list_connections(self):
        """Displays all active connections."""
        print("ID\tIP Address\tPort")
        for id, conn in self.connection_list.items():
            print(f"{id}\t{conn[1][0]}\t{conn[1][1]}")

    def terminate_connection(self, conn_id):
        """Terminates a connection with a peer."""
        if conn_id in self.connection_list:
            conn = self.connection_list[conn_id][0]
            self.inputs.remove(conn)
            conn.close()
            del self.connection_list[conn_id]
            print(f"Connection {conn_id} terminated.")
        else:
            print(f"No connection with ID {conn_id}")

    def send_message(self, conn_id, message):
        """Sends a message to a peer."""
        if conn_id in self.connection_list:
            conn = self.connection_list[conn_id][0]
            try:
                conn.sendall(message.encode())
                print(f"Message sent to {conn_id}")
            except Exception as e:
                print(f"Failed to send message to {conn_id}. Error: {e}")
        else:
            print(f"No connection with ID {conn_id}")

    def handle_received_message(self, conn, message):
        """Handles incoming messages from peers."""
        sender_info = None
        for id, c in self.connection_list.items():
            if c[0] == conn:
                sender_info = (id, c[1][0], c[1][1])
                break
        if sender_info:
            print(f"\nMessage received from {sender_info[1]}")
            print(f"Sender's Port: {sender_info[2]}")
            print(f"Message: \"{message}\"")
        else:
            print(f"\nReceived message from unknown sender.")

    def remove_connection(self, conn):
        """Removes a connection when it's closed by the peer."""
        for id, c in list(self.connection_list.items()):
            if c[0] == conn:
                self.inputs.remove(conn)
                conn.close()
                del self.connection_list[id]
                print(f"Connection {id} closed by peer.")
                break

    def exit(self):
        """Closes all connections and exits the application."""
        print("Closing all connections and exiting...")
        self.running = False
        for conn in self.inputs:
            if conn != self.server:
                conn.close()
        self.server.close()
        sys.exit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python chat.py <port>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
        host = socket.gethostbyname(socket.gethostname())
        peer = Peer(host, port)
        handle_help()
        peer.start_server()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
