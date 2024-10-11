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

#connection_list = {}

def get_my_ip():
        # Gets name of pc
        hostname = socket.gethostname()
        # Uses name of PC to find the current IP
        ip_address = socket.gethostbyname(hostname)
        print(f"Your IP address is: {ip_address}")


# PAss in port number from Peer
def get_my_port(port):
    print(f"My Port is: {port}")   

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
        # Used to get the program to loop
        self.running = True

    def start_server(self):
        # Starts the server to accept incoming connections.
        # Creates a server socket using socket.AF_INET (IPv4) and socket.SOCK_STREAM (TCP)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # binds (or connects) public host (pc) to the port given
        self.server.bind((self.host, self.port))
        # Listens to incoming connect requests, limited to 5 in it's listening queue before dropping requests
        self.server.listen(5)
        # inputs get watched by the server, adding/removing connections and decoding what is being sent to it
        self.inputs.append(self.server)
        print(f"Server started on {self.host}:{self.port}")

        # Start a thread to handle user input separately
        # We need daemon set true so the thread/input doesn't block the packets coming from the socket
        # This is also needed because otherwise windows blocks it due to security
        threading.Thread(target=self.handle_user_input, daemon=True).start()

        while True:
            readable, _, _ = select.select(self.inputs, [], [])
            for s in readable:
                #print("----------------*")
                
                # Has issues with port???
                # If the server socket is in the readable list, it means a new outside client is trying to connect.
                if s == self.server:
                    client_socket, addr = self.server.accept()

                    # The FIRST thing we send/receive is the listening port.
                    # So we capture that info here
                    listening_port = client_socket.recv(1024).decode()
                    #print(listening_port)
                    self.inputs.append(client_socket)# 2 Uncomment
                    # Kinda like in JS where a server is saying "wait im not done with info yet, come back later"
                    # when you dont use asyc/await
                    ####self.connection_list[self.id_counter] = ("pending", (addr[0], int(listening_port))) # 2 Uncomment
                    print(f"New connection from {addr[0]}:{listening_port} assigned ID {self.id_counter}")
                    # We connect to the peer who wants to talk with us
                    ####self.connect_to_peer(addr[0],int(listening_port))# TESTTT, UNCOMMENT when done testing

                    #print('1')
                    #client_socket.connect((addr[0], int(listening_port)))
                    #print('2')
                    #client_socket.sendall(str(self.port).encode())
                    threading.Thread(target= self.listen_to_connection, args=(client_socket, addr), daemon=True).start()
                    ###self.listen_to_connection(s)
                    #print('3')


                    # finally we add them to the list
                    self.connection_list[self.id_counter] = (client_socket, (addr[0], listening_port)) # 2 uncom
                    self.id_counter += 1 # 2 uncom
                    print('end')


        #self.run()

    '''
    def run(self):
        # Main loop to handle socket inputs and connections.
        while self.running:
            # Reading incoming data if any, if readable has stuff in it, then we go to loop
            readable, _, _ = select.select(self.inputs, [], [])
            for s in readable:
                #print("----------------*")
                
                # Has issues with port???
                # If the server socket is in the readable list, it means a new outside client is trying to connect.
                if s == self.server:
                    client_socket, addr = self.server.accept()

                    # The FIRST thing we send/receive is the listening port.
                    # So we capture that info here
                    listening_port = client_socket.recv(1024).decode()
                    #print(listening_port)

                    # not working yet, it's like the double connections are actually seperate
                    # Before adding to connection list, check if the connection already exists (IP and Port)
                    for conn in self.connection_list.values():
                        print('for loop in connection check: ',conn)
                        if conn[1][0] == addr[0] and conn[1][1] == listening_port:
                            print(f"Already connected to {addr[0]}:{listening_port}")
                            client_socket.close()
                            continue  # Connection already exists, so don't add again

                    self.inputs.append(client_socket)# 2 Uncomment
                    # Kinda like in JS where a server is saying "wait im not done with info yet, come back later"
                    # when you dont use asyc/await
                    ####self.connection_list[self.id_counter] = ("pending", (addr[0], int(listening_port))) # 2 Uncomment
                    print(f"New connection from {addr[0]}:{listening_port} assigned ID {self.id_counter}")
                    # We connect to the peer who wants to talk with us
                    ####self.connect_to_peer(addr[0],int(listening_port))# TESTTT, UNCOMMENT when done testing

                    print('1')
                    #client_socket.connect((addr[0], int(listening_port)))
                    print('2')
                    #client_socket.sendall(str(self.port).encode())
                    threading.Thread(target= Peer.listen_to_connection, args=(self,s), daemon=True).start()
                    ###self.listen_to_connection(s)
                    print('3')


                    # finally we add them to the list
                    self.connection_list[self.id_counter] = (client_socket, (addr[0], listening_port)) # 2 uncom
                    self.id_counter += 1 # 2 uncom
                    #del self.connection_list[self.id_counter]
                    #self.connection_list.popitem()
                    #self.id_counter -= 1
                    print(self.id_counter, type(self.connection_list))
                
    '''    
                            
    def listen_to_connection(self, client_socket, addr):
        print('listening ', client_socket)
        while True:
            try:
                
                # If a client socket is ready to read, it either has incoming data (recv()) 
                # or the connection is closed (in which case recv() returns empty).
                data = client_socket.recv(1024).decode()
                if data:
                    print('try get data')
                    self.handle_received_message(client_socket, data)
                else:
                   
                    try:
                        print('try remove')
                        self.remove_connection(client_socket)
                    except :
                        continue
            except:
                break
        # Connection was found to have no data, so we remove the connection.
        print('try remove')
        self.remove_connection(client_socket)
        

    # Handles user input in a separate thread. Meaning it can loop forever withour blocking
    def handle_user_input(self):
        while True:
            command = input().strip()
            self.handle_command(command)


    # Parse user commands here
    def handle_command(self, command):
        # We will have many args so we will split them
        tokens = command.split()
        if not tokens:
            return
        # First part of input should be main command hence [0]
        cmd = tokens[0].lower()

        # List of commands we have to deal with
        if cmd == 'help':
            handle_help()
        elif cmd == 'myip':
            get_my_ip()
        elif cmd == 'myport':
            get_my_port(self.port)
        elif cmd == 'connect':
            if len(tokens) != 3:
                print("Please use: connect <IP> <Port>")
                return
            self.connect_to_peer(tokens[1], int(tokens[2]))
        elif cmd == 'list':
            self.list_connections()
        elif cmd == 'terminate':
            if len(tokens) != 2:
                print("Correct input is: terminate <ID>")
                return
            self.terminate_connection(int(tokens[1]))
        elif cmd == 'send':
            # we use < 3 if they want to send many messages at once, idk if needed
            if len(tokens) < 3:
                print("Please use: send <ID> <Message>")
                return
            self.send_message(int(tokens[1]), ' '.join(tokens[2:]))
        elif cmd == 'exit':
            self.exit()
        else:
            print("Invalid command. Type 'help' for the list of commands and explainations.")


    # This connects correctly, but receiving port is wrong somwhere in code?
    # Connects to peer and does checks
    def connect_to_peer(self, ip, port):
        try:
            for conn in self.connection_list.values():
                #Check and make sure the connection is done connecting
                if conn[0] == "pending":
                    continue
                # Checks to make sure we don't connect twice to someone we are already connected with
                # This function will run twice on the 'initiating connector'/ person doing the connecting
                if conn[1][0] == ip and int(conn[1][1]) == port:
                    print("Already connected to this peer.")
                    return
            # We create a TCP connection with the client we are connecting to.
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))
            # We MUST send the listening port NOW, otherwise the other client will see the 
            # temp sending port the socket/server uses
            # We use str because ints may or may not end up decoded as something else on other side
            client_socket.sendall(str(self.port).encode())

            # Add it to inputs so we can listen to it as seen above
            self.inputs.append(client_socket)
            threading.Thread(target= self.listen_to_connection, args=(client_socket, (ip,int(port))), daemon=True).start()
            # Add new connection to the connection list too with id.
            self.connection_list[self.id_counter] = (client_socket, (ip, port))
            print(f"Connected to {ip}:{port} assigning them ID {self.id_counter}")
            self.id_counter += 1
            print("cp",self.id_counter)
        except Exception as e:
            print(f"FAILED to connect to {ip}:{port}. Error: {e}")


    # Function that deals with incoming messages from connected clients
    def handle_received_message(self, conn, message):
        # base sender info, assigned later
        sender_info = None
        # For the id and connection in connection dict
        for id, c in self.connection_list.items():
            # if this connection IP we found in the list is same as connection IP from params
            # we then assign sender info with the correct IP, port and ID. 
            if c[0] == conn:
                sender_info = (id, c[1][0], c[1][1])
                break
        # We have sender info so we show the message and who it's from
        if sender_info:
            print(f"\n\nMessage received from {sender_info[1]}")
            print(f"Sender's Port: {sender_info[2]}")
            print(f"Message: \"{message}\"")
        else:
            print(f"\nReceived message from unknown sender.")


    #Lists all connections
    def list_connections(self):
        print("ID\tIP Address\tPort")
        if len(self.connection_list.items()) > 0:
            for id, conn in self.connection_list.items():
                print(f"{id}\t{conn[1][0]}\t{conn[1][1]}")
        else:
            print("No connections detected!")
        print("\n")


    # Deletes / disconnects from a connection 
    def terminate_connection(self, conn_id):
        if conn_id in self.connection_list:
            conn = self.connection_list[conn_id][0]
            conn.shutdown(socket.SHUT_RDWR) 
            """
            # we get socket here
            conn = self.connection_list[conn_id][0]
            try:
                # Shut down the connection for both sending and receiving
                conn.shutdown(socket.SHUT_RDWR)  
                conn.close()  # Close the connection
            except Exception as e:
                # We can continue here now, we can ignore error.
                print(f"Error shutting down connection: {e}")
                
            """
            self.inputs.remove(conn)
            del self.connection_list[conn_id]
            print(f"Connection {conn_id} terminated.")
        else:
            print(f"No connection with ID {conn_id}")


    # Send message given connection id and message
    def send_message(self, conn_id, message):
        # Find connection in list
        if conn_id in self.connection_list:
            # we grab the socket to send to
            conn = self.connection_list[conn_id][0]
            #print(conn,"\n",self.connection_list,"\n")
            try:
                # we send ALL message data and encode it 
                # we must send ALL since 'send' will not always send everything at once and would need to be looped weird
                conn.sendall(message.encode())
                print(f"Message sent to {conn_id}")
            except Exception as e:
                print(f"Failed to send message to {conn_id}. Error: {e}")
        else:
            print(f"No connection with ID {conn_id}")


    # Removes connection when it's closed. But we run this one if the OTHER client disconnects
    # We can't tell otherwise who disconnected if we dont have multiple functions for this
    def remove_connection(self, conn):
        # conn is the socket the other client is on
        # we check each connection in list to find which we must disconnect
        try:
            for id, c in list(self.connection_list.items()):

                if c[0] == conn:
                    self.inputs.remove(conn)
                    # Try shutdown here too?
                    #conn.close()
                    del self.connection_list[id]
                    print(f"Connection {id} closed by peer.")
                    break

        except Exception as e:
            print(f"Error shutting down connection: {e}")

    # Ran when exiting the CLI
    def exit(self):
        print("\nTelling all connections of shutdown and exiting...")
        # Should Stop running the threads and main loop
        self.running = False
        # close all connections
        for conn in self.inputs:
            if conn != self.server:
                self.inputs.remove(conn)
                # was close(), trying shutdown though
                #conn.shutdown(socket.SHUT_RDWR) 
                #self.terminate_connection()
        # close server now, then we can exit
        #print('we out')
        self.inputs.pop(0)
        self.server.close()
        sys.exit()




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





def start_file():
    if len(sys.argv) != 2:
        print("Type to start is: python chat.py <port>")
        sys.exit(1)

    try:
        # we get port in the second [1] arg
        port = int(sys.argv[1])
        # IP is got by hostname, EX: IP of my pc MSI is xxx.xxx.xxx.xx
        host = socket.gethostbyname(socket.gethostname())
        peer = Peer(host, port)
        # print help commands so users know how to use
        handle_help()
        threading.Thread(target=peer.start_server(), daemon=True).start()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


start_file()
