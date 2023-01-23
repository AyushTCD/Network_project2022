#Computer Networks
#Oliver Juchnevicius 18319392
#Vidang Mishra 21355044
#Made with reference to
#https://realpython.com/python-sockets/
#https://github.com/macsnoeren/python-p2p-network

import time

from source import node

# Define Node 1
n = node("10.35.70.26", 33333, 1)

c = input('Enter y to start thread\n')
while c != 'y':
    c = input('Enter y to start thread\n')

n.start()
time.sleep(10)
n.connectTo("10.35.70.40", 33333)

msg = input('Enter Message to Send or Type >end< to Stop\n')

while msg != "end":
    n.broadcast(msg)
    msg = input('Enter Message to Send or Type >end< to Stop\n')

# Stop Threads
n.stop()

print("End of Network Test")
