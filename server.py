# 
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# server.py - the server program for taking request from the client and 
#             send the requested file back to the client
#
import socket
import os

serverPort = 50000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)
print("Server is ready to recieve connections")

""" Old open_file function with try except
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
"""

def open_file(path, connectionSocket):
    if not os.path.exists(path):
        connectionSocket.send("error: file not found".encode())
        connectionSocket.close() # DC from client if fail
        print("error: open file failed")
        return False
    file = open(path, "rb")

    # To separate success message from main file
    connectionSocket.send("success: file exist".encode())
    client_confirm = connectionSocket.recv(1024).decode()
    if client_confirm != "SUCCESS":
        file.close()
        connectionSocket.close() # DC from client if fail
        print("error: client connection failed")
        return False
    print("success: file opened")
    return file

while True:
    # recieve manifest file request
    connectionSocket, clientAddr = serverSocket.accept()
    video_name = connectionSocket.recv(1024).decode()
    mpd_path = "./data/" + video_name + "/manifest.mpd" # manifest file

    mpd_file = open_file(mpd_path, connectionSocket)
    if not mpd_file:
        continue

    # sending mpd file
    while True:
        chunk = mpd_file.read(4096)
        if not chunk:
            break
        connectionSocket.send(chunk) # encoding not needed for file opened in binary
    
    mpd_file.close()

    connectionSocket.close()