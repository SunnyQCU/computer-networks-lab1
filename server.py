# 
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# server.py - the server program for taking request from the client and 
#             send the requested file back to the client
#
import socket
import os

FSIZE_BYTES = 128

def open_file(path, connectionSocket):
    if not os.path.exists(path):
        send_msg(connectionSocket, "error: file not found")
        connectionSocket.close() # DC from client if fail
        print("error: open file failed")
        return False
    send_msg(connectionSocket, "success: file exist")
    file = open(path, "rb")
    return file

def receive_req(connectionSocket): #protocol
    #first get file size
    # file_size_raw = connectionSocket.recv(FSIZE_BYTES)
    bytes_read = 0
    file_size_raw = b""
    while (bytes_read < FSIZE_BYTES):
        chunk = connectionSocket.recv(FSIZE_BYTES - len(file_size_raw)) #only get remaing
        file_size_raw += chunk
        bytes_read += len(chunk)

    file_size = int(file_size_raw.decode('utf-8')); # file_size always 10 bytes

    bytes_read = 0
    data = b""
    while (bytes_read < file_size):
        chunk = connectionSocket.recv(file_size - len(data)) #only get remaing
        data += chunk
        bytes_read += len(chunk)

    # bytes_read = 0
    # data = b""
    # while (bytes_read < file_size):
    #     chunk = connectionSocket.recv(4096)
    #     data += chunk
    #     bytes_read += len(chunk)
    return data.decode('utf-8')

def send_file(connectionSocket, file):
    # set the data
    data = file.read()
    byte_size = len(data)

    print(f"SERVER Size in bytes: {byte_size}")
    req_size_bytes = (str(byte_size).zfill(FSIZE_BYTES)).encode('utf-8')
    print(f"SERVER Byte size: {req_size_bytes}")
    connectionSocket.sendall(req_size_bytes)

    res = receive_req(connectionSocket) #return confirmation
    
    connectionSocket.sendall(data)
    return

def send_msg(connectionSocket, msg):
    # set the data
    msg_encoded = msg.encode('utf-8')
    byte_size = len(msg_encoded)

    req_size_bytes = (str(byte_size).zfill(FSIZE_BYTES)).encode('utf-8')
    connectionSocket.sendall(req_size_bytes)

    connectionSocket.sendall(msg_encoded)
    return

#start here

serverPort = 50000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)
print("Server is ready to recieve connections")

while True:
    # recieve manifest file request
    connectionSocket, clientAddr = serverSocket.accept()
    video_name = receive_req(connectionSocket)
    # video_name = connectionSocket.recv(1024).decode()
    mpd_path = "./data/" + video_name + "/manifest.mpd" # manifest file

    if not os.path.exists(mpd_path):
        send_msg(connectionSocket, "error: file not found")
        print("error: open file failed")
        connectionSocket.close() # DC from client if fail
        continue
    send_msg(connectionSocket, "success: file exist")
    mpd_file = open(mpd_path, "rb")

    if not mpd_file: 
        continue

    send_file(connectionSocket, mpd_file)
    print("mpd sent")
    # connectionSocket.sendall(mpd_data) #to mpd_text = recieve_Data(clientSocket).decode()
    mpd_file.close() # done with MPD file

    print("before while loop")
    while (True):
        vchunk_name = receive_req(connectionSocket) #recieve chunk_name
        vchunk_path = "./data/" + video_name + "/chunks/" + vchunk_name + ".m4s"
        print(vchunk_path)

        if not os.path.exists(vchunk_path):
            send_msg(connectionSocket, "error: file not found")
            connectionSocket.close() # DC from client if fail
            print("error: open file failed")
            break
        send_msg(connectionSocket, "success: file exist")
        vchunk_file = open(vchunk_path, "rb")

        if not vchunk_file: 
            vchunk_file.close() # done with MPD file
            break # open_file automatically closes client
        send_file(connectionSocket, vchunk_file) #send the video
        vchunk_file.close() # done with MPD file

    print("Server disconnected.")
    connectionSocket.close()



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

"""

To separate success message from main file
    send_data(connectionSocket, "success: file exist")
    connectionSocket.send("success: file exist".encode())
    client_confirm = connectionSocket.recv(1024).decode()
    if client_confirm != "SUCCESS":
        file.close()
        connectionSocket.close() # DC from client if fail
        print("error: client connection failed")
        return False
    
    print("success: file opened")
    return file

    client_confirm = connectionSocket.recv(1024).decode()
    if client_confirm != "SUCCESS":
        connectionSocket.close() # DC from client if fail
        print("error: client connection failed")
        continue


    sending mpd file
    mpd_data = mpd_file.read()'

 connectionSocket.sendall(vchunk_data)
        while True: # sends the entire chunk
            vchunk = mpd_file.read(4096)
            if not vchunk:
                break
            connectionSocket.send(vchunk)


    while True:
        mpd_chunk = mpd_file.read(4096)
        if not mpd_chunk:
            connectionSocket.send(mpd_chunk) # last dead chunk
            break
        connectionSocket.send(mpd_chunk) # encoding not needed for file opened in binary
    mpd_file.close() # done with MPD file

"""