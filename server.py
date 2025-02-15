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

    # confirm accept and ensure data separation
    client_confirm = connectionSocket.recv(1024).decode()
    if client_confirm != "SUCCESS":
        connectionSocket.close() # DC from client if fail
        return -1

    return file

while True:
    # recieve manifest file request
    connectionSocket, clientAddr = serverSocket.accept()
    video_name = connectionSocket.recv(1024).decode()
    mpd_request = "./data/" + video_name + "/manifest.mpd" # manifest file

    # opening file
    mpd_file = open_file(mpd_request, connectionSocket)
    if mpd_file == -1:
        continue # reloop if no file or file failed opening

    # sending mpd file
    while True:
        chunk = mpd_file.read(4096)
        if not chunk:
            break
        connectionSocket.send(chunk) # encoding not needed for file opened in binary
    
    mpd_file.close()
    # mpd_file = open(mpd_request, "rb") # open for reading in binary
    # connectionSocket.send(mpd_file.encode())

    # connectionSocket.send()
    connectionSocket.close()