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

def client(server_addr, server_port, video_name, alpha, chunks_queue):
    # setup socket and files
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((server_addr, server_port))
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    # send request for manifest file of video and recieve
    clientSocket.send(video_name.encode())
    result = clientSocket.recv(64).decode()
    print(result)
    if result == "error: not found" or result == "error: IO failed": #failed
        clientSocket.close() #DC from server if not found
        return -1
        
    
    #mpd_file = clientSocket.recv(4096)

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

    clientSocket.close()
    return

    # to visualize the adaptive video streaming, store the chunk in a temporary folder and
    # pass the path of the chunk to the video player
    # 
    # create temporary directory if not exist
    # if not os.path.exists("tmp"):
    #     os.makedirs("tmp")
    # # write chunk to the temporary directory
    # with open(f"tmp/chunk_0.m4s", "wb") as f:
    #     f.write(chunk)
    # # put the path of the chunk to the queue
    # chunks_queue.put(f"tmp/chunk_0.m4s")


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
