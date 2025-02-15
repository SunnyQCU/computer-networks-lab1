# 
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# server.py - the server program for taking request from the client and 
#             send the requested file back to the client
#
import socket
serverPort = 50000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)
print("Server is ready to recieve connections")

def open_file(request, connectionSocket):
    try:
        file = open(request, "rb")
        success_msg = "success: file exist"
        connectionSocket.send(success_msg.encode())
        return file
    except FileNotFoundError:
        err_msg = "error: not found"
        connectionSocket.send(err_msg.encode())
        connectionSocket.close() # DC from client if fail
        return -1
    except IOError:
        err_msg = "error: IO failed"
        connectionSocket.send(err_msg.encode())
        connectionSocket.close()
        return -1

while True:
    # recieve manifest file request
    connectionSocket, clientAddr = serverSocket.accept()
    video_name = connectionSocket.recv(1024).decode()
    mpd_request = "./data/" + video_name + "/manifest.mpd" # manifest file

    # opening file
    file = open_file(mpd_request, connectionSocket)
    if file == -1:
        continue 
    
    # mpd_file = open(mpd_request, "rb") # open for reading in binary
    # connectionSocket.send(mpd_file.encode())

    # connectionSocket.send()
    connectionSocket.close()