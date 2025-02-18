# 
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# server.py - the server program for taking request from the client and 
#             send the requested file back to the client
#
import socket
import os
import sys

FSIZE_BYTES = 32

def recv_exactly(connectionSocket, size):
    """ Ensures recv downloads exact number of bytes. 
        No more, no less.
    
    Keyword arguments:
    connectionSocket -- the connecting client's socket
    size -- number of bytes to recieve
    """
    bytes_read = 0
    data = b""
    while (bytes_read < size):
        chunk = connectionSocket.recv(size - len(data)) #only get remaing
        data += chunk
        bytes_read += len(chunk)
    return data

def open_file(connectionSocket, path):
    """ Opens the requested file. Returns False if it doesn't exist.
    
    Keyword arguments:
    connectionSocket -- the connecting client's socket
    path -- path to the file to be opened
    """
    if not os.path.exists(path):
        send_msg(connectionSocket, "error: file not found")
        connectionSocket.close() # DC from client if fail
        return False
    send_msg(connectionSocket, "success: file exist")
    file = open(path, "rb")
    return file

def receive_req(connectionSocket): #protocol
    """ Processes and returns recieved string from client
    
    Keyword arguments:
    connectionSocket -- the connecting client's socket
    """
    file_size_raw = recv_exactly(connectionSocket, FSIZE_BYTES)
    file_size = int(file_size_raw.decode('utf-8')); # file_size always 10 bytes
    data = recv_exactly(connectionSocket, file_size)
    return data.decode('utf-8')

def send_file(connectionSocket, file):
    """ Sends file to client
    
    Keyword arguments:
    connectionSocket -- the connecting client's socket
    file -- file to send
    """
    data = file.read()
    byte_size = len(data)

    req_size_bytes = (str(byte_size).zfill(FSIZE_BYTES)).encode('utf-8')
    connectionSocket.sendall(req_size_bytes)
    
    connectionSocket.sendall(data)
    return

def send_msg(connectionSocket, msg):
    """ Sends string to client
    
    Keyword arguments:
    connectionSocket -- the connecting client's socket
    msg -- msg to send
    """
    msg_encoded = msg.encode('utf-8')
    byte_size = len(msg_encoded)
    req_size_bytes = (str(byte_size).zfill(FSIZE_BYTES)).encode('utf-8')
    connectionSocket.sendall(req_size_bytes)
    connectionSocket.sendall(msg_encoded)
    return

def server(serverPort):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)

    while True:
        connectionSocket, clientAddr = serverSocket.accept()
        video_name = receive_req(connectionSocket) # recieve manifest file request
        mpd_path = "./data/" + video_name + "/manifest.mpd"
        mpd_file = open_file(connectionSocket, mpd_path)

        if not mpd_file: 
            continue

        send_file(connectionSocket, mpd_file)
        mpd_file.close()

        while (True):
            vchunk_name = receive_req(connectionSocket) # recieve chunk_name
            vchunk_path = "./data/" + video_name + "/chunks/" + vchunk_name + ".m4s"
            vchunk_file = open_file(connectionSocket, vchunk_path)
            if not vchunk_file: 
                break
            send_file(connectionSocket, vchunk_file)
            vchunk_file.close()

        connectionSocket.close()
    return

if __name__ == '__main__':
    listen_port = int(sys.argv[1])
    server(listen_port)