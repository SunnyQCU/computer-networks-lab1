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
        send_file(connectionSocket, "error: file not found")
        # connectionSocket.send("error: file not found".encode())
        connectionSocket.close() # DC from client if fail
        print("error: open file failed")
        return False
    send_file(connectionSocket, "success: file exist")
    file = open(path, "rb")
    return file
    # To separate success message from main file
    # send_data(connectionSocket, "success: file exist")
    # connectionSocket.send("success: file exist".encode())
    # client_confirm = connectionSocket.recv(1024).decode()
    # if client_confirm != "SUCCESS":
    #     file.close()
    #     connectionSocket.close() # DC from client if fail
    #     print("error: client connection failed")
    #     return False
    
    # print("success: file opened")
    # return file

def receive_req(connectionSocket): #protocol
    #first get file size
    file_size = int(connectionSocket.recv(10).decode()); # file_size always 10 bytes
    bytes_read = 0
    data = b""
    while (bytes_read < file_size):
        chunk = connectionSocket.recv(4096)
        data += chunk
        bytes_read += 4096
    return data.decode()

def send_file(connectionSocket, file):
    # set the data
    data = None
    if isinstance(file, str): 
        data = file.encode()
    else: 
        data = file.read()
    byte_size = len(data)

    print(f"SERVER Size in bytes: {byte_size}")
    req_size_bytes = str(byte_size).zfill(10)
    connectionSocket.send(req_size_bytes.encode())
    connectionSocket.sendall(data)
    return

while True:
    # recieve manifest file request
    connectionSocket, clientAddr = serverSocket.accept()
    video_name = receive_req(connectionSocket)
    # video_name = connectionSocket.recv(1024).decode()
    mpd_path = "./data/" + video_name + "/manifest.mpd" # manifest file
    mpd_file = open_file(mpd_path, connectionSocket)
    if not mpd_file: 
        continue

    # sending mpd file
    # mpd_data = mpd_file.read()

    print("right before send")
    send_file(connectionSocket, mpd_file)
    # connectionSocket.sendall(mpd_data) #to mpd_text = recieve_Data(clientSocket).decode()
    mpd_file.close() # done with MPD file

    print("before while loop")
    while (True):
        vchunk_name = receive_req(connectionSocket) #recieve chunk_name
        vchunk_path = "./data/" + video_name + "/chunks/" + vchunk_name + ".m4s"
        print(vchunk_path)
        vchunk_file = open_file(vchunk_path, connectionSocket)
        if not vchunk_file: 
            send_file(connectionSocket, "error: file not found")
            print("no such file")
            break #open_file automatically closes client
        # vchunk_data = vchunk_file.read()
        send_file(connectionSocket, vchunk_file)
        # connectionSocket.sendall(vchunk_data)
        # while True: # sends the entire chunk
        #     vchunk = mpd_file.read(4096)
        #     if not vchunk:
        #         break
        #     connectionSocket.send(vchunk)
        vchunk_file.close() # done with MPD file

    connectionSocket.close()


    # client_confirm = connectionSocket.recv(1024).decode()
    # if client_confirm != "SUCCESS":
    #     connectionSocket.close() # DC from client if fail
    #     print("error: client connection failed")
    #     continue


    # while True:
    #     mpd_chunk = mpd_file.read(4096)
    #     if not mpd_chunk:
    #         connectionSocket.send(mpd_chunk) # last dead chunk
    #         break
    #     connectionSocket.send(mpd_chunk) # encoding not needed for file opened in binary
    # mpd_file.close() # done with MPD file