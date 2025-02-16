# 
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# client.py - the client program for sending request to the server and play the received video chunks
#

import threading
from queue import Queue
# from video_player import play_chunks #only needed for video laying
import sys

# added myself
import socket
import os
import xml.etree.ElementTree as ET #ok according to assignment

"""
    the client function
    write your code here

    arguments:
    server_addr -- the address of the server
    server_port -- the port number of the server
    video_name -- the name of the video
    alpha -- the alpha value for exponentially-weighted moving average
    chunks_queue -- the queue for passing the path of the chunks to the video player

"""
    
def receive_data(clientSocket): #protocol
    #first get file size
    file_size = int(clientSocket.recv(10).decode()); # file_size always 10 bytes
    bytes_read = 0
    data = b""
    while (bytes_read < file_size):
        chunk = clientSocket.recv(4096)
        data += chunk
        bytes_read += 4096
    try: # string or byte file
        data = data.decode()
    except UnicodeDecodeError:
        pass
    return data

def send_req(clientSocket, req):
    byte_size = len(req.encode())
    print(f"Size in bytes: {byte_size}")
    req_size_bytes = str(byte_size).zfill(10)
    clientSocket.send(req_size_bytes.encode()) # send request size

    clientSocket.send(req.encode()) # send request
    return

def check_video(clientSocket, video_name):
    send_req(clientSocket, video_name)
    mpd_file_res = receive_data(clientSocket)
    #error checking below
    print(mpd_file_res + '\n')
    if mpd_file_res == "error: file not found":
        clientSocket.close() #DC from server if not found
        return False #close if it doesn't exist
    return True

def parse_bitrates(clientSocket, mpd_text):
    root = ET.fromstring(mpd_text)
    bitrates = [int(rep.get("bandwidth")) for rep in root.findall(".//Representation")]
    for b in bitrates: 
        print(b)
    return bitrates

def client(server_addr, server_port, video_name, alpha, chunks_queue):
    # setup socket and files
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((server_addr, server_port))

    if not check_video(clientSocket, video_name): 
        print("No video.")
        return False # video doesn't exist

    mpd_text = receive_data(clientSocket) # from connectionSocket.sendall(mpd_data)
    print(mpd_text) 

    bitrates = parse_bitrates(clientSocket, mpd_text)
    bitrates.sort() #lowest to highest bitrate sorted

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    chunk_num = 0
    bitrate = bitrates[0] #temporary lowest bitrate
    while (True): #loop of .m4s files
        chunk_name = video_name + "_" + str(bitrate) + "_" + str(chunk_num).zfill(5)
        print(chunk_name)
        send_req(clientSocket, chunk_name)
        res = receive_data(clientSocket)
        if res == "error: file not found" or res == "error: IO failed":
            clientSocket.close() #DC from server if not found
            break #last file

        curr_file = open(f"tmp/chunk_{chunk_num}.m4s", "wb")
        data = receive_data(clientSocket)
        curr_file.write(data)
        chunks_queue.put(f"tmp/chunk_{chunk_num}.m4s")
        chunk_num += 1

    print("Client session termiated.")
    clientSocket.close()
    return

"""
    to visualize the adaptive video streaming, store the chunk in a temporary folder and
    pass the path of the chunk to the video player
    
    create temporary directory if not exist
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    # write chunk to the temporary directory
    with open(f"tmp/chunk_0.m4s", "wb") as f:
        f.write(chunk)
    # put the path of the chunk to the queue
    chunks_queue.put(f"tmp/chunk_0.m4s")
"""

# parse input arguments and pass to the client function
if __name__ == '__main__':
    server_addr = sys.argv[1]
    server_port = int(sys.argv[2])
    video_name = sys.argv[3]
    alpha = float(sys.argv[4])

    # init queue for passing the path of the chunks to the video player
    chunks_queue = Queue()
    # start the client thread with the input arguments
    client_thread = threading.Thread(target = client, args =(server_addr, server_port, video_name, alpha, chunks_queue))
    client_thread.start()
    # start the video player
    # play_chunks(chunks_queue) //only needed for video playing


# def check_video(clientSocket, video_name):
#     clientSocket.send(video_name.encode())
#     mpd_file_res = clientSocket.recv(64).decode()
#     print(mpd_file_res + '\n')
#     if mpd_file_res == "error: file not found" or mpd_file_res == "error: IO failed":
#         clientSocket.close() #DC from server if not found
#         return False #close if it doesn't exist
#     return True