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

def check_video(clientSocket, video_name):
    clientSocket.send(video_name.encode())
    mpd_file_res = clientSocket.recv(64).decode()
    print(mpd_file_res + '\n')
    if mpd_file_res == "error: not found" or mpd_file_res == "error: IO failed":
        clientSocket.close() #DC from server if not found
        return False #close if it doesn't exist
    return True
    
def recieve_data(clientSocket):
    # Actually recieve and print mpd file
    mpd_data = b""
    while (True): #keep on collecting data till there's none left
        chunk = clientSocket.recv(4096)
        if not chunk: #finished receiving data
            print("Done receiving\n")
            break
        mpd_data += chunk
    return mpd_data

def client(server_addr, server_port, video_name, alpha, chunks_queue):
    # setup socket and files
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((server_addr, server_port))
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    if not check_video(clientSocket, video_name): return False # video doesn't exist
    
    # Acknowledged recieved
    clientSocket.send("SUCCESS".encode())
    
    mpd_text = recieve_data(clientSocket).decode() # mpd file
    print(mpd_text) 
    

    # print(mpd_file) #can it actually print??

    clientSocket.close()
    return


    """
    chunk_num = 0
    while (True): #keep on collecting data till there's none left
        chunk = clientSocket.recv(1024)
        if not chunk: #finished receiving data
            break
        with open(f"tmp/chunk_{chunk_num}.m4s", "wb") as f:
            f.write(chunk)
        chunks_queue.put(f"tmp/chunk_{chunk_num}.m4s")
        chunk_num += 1
    """

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
