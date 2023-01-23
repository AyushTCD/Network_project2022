#Computer Networks
#Oliver Juchnevicius 18319392
#Vidang Mishra 21355044
#Made with reference to
#https://realpython.com/python-sockets/
#https://github.com/macsnoeren/python-p2p-network

import socket
import time
import threading

# This class defines a connection
class connection(threading.Thread):

    def __init__(self, origin, sock, id, host, port):
        super (connection, self).__init__()

        self.host = host # Destination Host address
        self.port = port # Destination Port number
        self.id = str(id) # ID of node for our network
        self.origin = origin # Originating Node
        self.sock = sock # Socket
        self.end = threading.Event() # Used for thread status and thread end
        self.sock.settimeout(300) # Set time out for socket
    
    def send(self, data): # Send a data packet
        try:
            self.sock.sendall(data.encode('utf-8')) # Send data with encoding
            print(f"Sending from {self.origin.id}\n {data} ")
        except:
            print(f"Sending failed from {self.origin.id} to {self.id} ")
            self.stop() 
    
    def stop(self): # Stop thread 
        self.end.set() # Set threading event to set
        print(f"Connection closed: {self.origin.id} and {self.id}")
    
    def run(self): # Run by thread

        while not self.end.is_set(): # While thread status not set
            try:
                data = self.sock.recv(4096).decode('utf-8') # Try recieve data from socket
            except BlockingIOError:
                print(f"{self.id} Blocking Error ") # Handle Blocking Error
            except socket.timeout:
                print(f"{self.id} timed out ") # Handle Time Out
            else:
                if data:
                    print(f"{self.origin.id} has recieved:\n {data} ")  # Print data from recv
                else:
                    data = None 
        
        self.sock.settimeout(None)
        self.sock.close() # Close socket

# Defines a node
class node(threading.Thread):

    def __init__(self, host, port, id):
        super(node, self).__init__()

        self.host = host # Node Host Address
        self.port = port # Node Port Number
        self.id = str(id) # ID given to node
        self.nodesIn = [] # Array containing connected nodes inbound
        self.nodesOut = [] # Array containing connected nodes outbound
        self.end = threading.Event() # Thread status container

        # Initiate server and socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(300.0)
        self.sock.listen(1)

    def connectTo(self, host, port): # Connect to another node

        if host == self.host and port == self.port: # Exclude self connection
            print(f"Node {self.id} Cannot connect to self ")
            return False

        for node in self.nodesOut: # Excluding existing nodes
            if node.host == host and node.port == port:
                print(f"Node {node.id} already connected ")
                return True
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Connect to a socket
            sock.connect((host,port))
            print(f"{self.id} Connecting to {host} through port {port} ")

            sock.send(self.id.encode('utf-8')) # Send ID
            cnctId = sock.recv(4096).decode('utf-8') # Receive ID

            if self.id == cnctId: # Handle self connection
                print(f"Node {self.id} Cannot connect to self ")
                sock.send("Connection closing".encode('utf-8'))
                return True
            
            for node in self.nodesIn: # Handle existing connection
                if node.host == host and node.id == cnctId:
                    print(f"{self.id} is already connected to {node.id}")
                    sock.send("Connection closing".encode('utf-8'))
                    return True
            
            connection_thread = self.connectNew(sock, cnctId, host, port) # Initiate connection thread
            connection_thread.start() # Start running connection thread

            self.nodesOut.append(connection_thread) # Store created connection in array
            print(f"Connected to {cnctId} from {self.id} ")

            return True
        
        except: # Handle failed connection
            print(f"{self.id} Failed to establish TCP connection with {host} on {port} ")
            return False

    def stop(self): # Function to set thread status to stop
        print(f"{self.id} is stopping ")
        self.end.set()

    def broadcast(self, chunk): # Send message to all connections

        for n in self.nodesIn:
            n.send(chunk)
        
        for n in self.nodesOut:
            n.send(chunk)

    def connectNew(self, socket, id, host, port): # Function to return connection class
        return connection(self, socket, id, host, port)
        
        
    def run(self):

        while not self.end.is_set(): # While thread status is not set
            try:
                connection, address = self.sock.accept() # Try accept conenction from socket

                connected_node_id = connection.recv(4096).decode('utf-8') # Decode received ID
                connection.send(self.id.encode('utf-8')) # Send your own ID

                thread_client = self.connectNew(connection, connected_node_id, address[0], address[1]) # Create new connection with values returned by .accept()
                thread_client.start() # Start new thread

                self.nodesIn.append(thread_client) # Add new connection to Inbound array

            except socket.timeout: # Handle timeout
                print("Socket Timeout")
                self.stop(self)
            except: 
                raise RuntimeError 

            time.sleep(0.01)

        # End all connection threads when stopping node
        for connection_thread in self.nodesIn:
            print(f"Stop & Join {connection_thread.id} ")
            connection_thread.stop()
            connection_thread.join()
        
        for connection_thread in self.nodesOut:
            print(f"Stop & Join {connection_thread.id} ")
            connection_thread.stop()
            connection_thread.join()

        # Close socket
        self.sock.settimeout(None)
        self.sock.close()
        print(f"{self.id} Node stopped ")
