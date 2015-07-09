import socket

# IP_ADDR = '192.168.1.109'
# IP_ADDR = '192.168.1.110'
IP_ADDR = '192.168.1.107'
# IP_ADDR = '127.0.0.1'
DEFAULT_PORT = 9750

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

def connect():

    s.connect((IP_ADDR, DEFAULT_PORT))

def reconnect():
    s.close()
    s.connect((IP_ADDR, DEFAULT_PORT))

def y():
    s.send('y')

def n():
    s.send('n')

def print_xbee():
    print s.recv(1024)
