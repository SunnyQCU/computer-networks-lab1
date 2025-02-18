# 
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# client.py - the client program for sending request to the server and play the received video chunks
#

import threading
from queue import Queue
# from video_player import play_chunks #only needed for video playing
import sys

# Below imports are ones I added myself
import socket
import os
import xml.etree.ElementTree as ET
import time

FSIZE_BYTES = 32

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
    
def recv_exactly(clientSocket, size):
    """ Ensures recv downloads exact number of bytes. 
        No more, no less.
    
    Keyword arguments:
    clientSocket -- the client's socket
    size -- number of bytes to recieve
    """
    bytes_read = 0
    data = b""
    while (bytes_read < size):
        chunk = clientSocket.recv(size - len(data)) #only get remaing
        data += chunk
        bytes_read += len(chunk)
    return data

def send_req(clientSocket, req): #ONLY FOR STRING REQUESTS
    """ Send string to server

    Keyword arguments:
    clientSocket -- the client's socket
    req -- string to send
    """
    req_encoded = req.encode('utf-8')
    byte_size = len(req_encoded)

    req_size_bytes = (str(byte_size).zfill(FSIZE_BYTES)).encode() #b"00000080"
    clientSocket.sendall(req_size_bytes) # send request size

    clientSocket.sendall(req.encode('utf-8')) # send request
    return

def receive_msg(clientSocket): #protocol
    """ Processes and returns received string from server

    Keyword arguments:
    clientSocket -- the client's socket
    """
    file_size_raw = recv_exactly(clientSocket, FSIZE_BYTES)
    print(f"Raw received bytes: {file_size_raw}")
    file_size = int(file_size_raw.decode('utf-8'))
    data = recv_exactly(clientSocket, file_size)
    return data.decode('utf-8')

def receive_data(clientSocket): #protocol
    """ Processes and returns recieved file data from server

    Keyword arguments:
    clientSocket -- the client's socket
    """
    file_size_raw = recv_exactly(clientSocket, FSIZE_BYTES)
    print(f"DATA Raw received bytes: {file_size_raw}")
    file_size = int(file_size_raw.decode('utf-8'))
    data = recv_exactly(clientSocket, file_size)
    return data

def parse_bitrates(mpd_text):
    """ Parses mpd_file for bitrates and put them into a sorted array

    Keyword arguments:
    mpd_text -- the mpd_file in string format
    """
    root = ET.fromstring(mpd_text)
    bitrates = [int(rep.get("bandwidth")) for rep in root.findall(".//Representation")]
    for b in bitrates: 
        print(b)
    bitrates.sort()
    return bitrates

def calc_tnew(chunk_size, tstart, tfin):
    """ Calculates the throughput for the new chunk

    Keyword arguments:
    chunk_size -- size of chunk in bytes
    tstart -- chunk request time
    tfin -- chunk download finish time
    """
    return (chunk_size * 8) / (tfin - tstart) # bits/second

def update_tcurr(tcurr, alpha, tnew): # len(data) is the chunk size
    """ Updates the current throughput

    tcurr -- current throughput from one chunk before
    alpha -- constant provided in argument line (between 0 and 1)
    tnew -- throughput for the new chunk
    """
    return alpha * tnew + (1 - alpha) * tcurr

def update_bitrate(tcurr, bitrates):
    """ Determines bitrate to request for next chunk.
        Requests the bitrate that is less or equal to
        throughput / 1.5 so avg throughput is at least 1.5
        times bitrate.

    tcurr -- current throughput (new throughput included)
    bitrates -- array of sorted bitrates
    """
    maxbitrate = tcurr / 1.5 # throughput >= 1.5 * bitrate
    bitrate = bitrates[0] # default lowest bitrate
    i = 0
    while(i < len(bitrates) and maxbitrate >= bitrates[i]):
        bitrate = bitrates[i]
        i += 1
    return bitrate

def log_entry(tconnect, tstart, tfin, tput, tavg, bitrate, chunk_name):
    """ Writes the calculations of the current chunk to the log.txt file

    tconnect: Time since connecting to network
    tstart: chunk request time
    tfin: chunk download finish time
    tput: The tnew for the current chunk
    tavg: The tcurr including the current chunk
    bitrate: bitrate requested from the server
    chunk_name: name of the chunk requested from the server
    """
    chunk_name = chunk_name + ".m4s"
    duration = tfin - tstart
    log_entry = f"{tconnect} {duration} {tput} {tavg} {bitrate} {chunk_name}\n"
    log = open("log.txt", "a") #opens for writing
    log.write(log_entry)
    log.close()
    return

def client(server_addr, server_port, video_name, alpha, chunks_queue):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((server_addr, server_port))
    tnet_start = time.time()
    if os.path.exists("log.txt"):
        os.remove("log.txt")

    # check video existance
    send_req(clientSocket, video_name)
    mpd_file_res = receive_msg(clientSocket)
    if mpd_file_res == "error: file not found":
        clientSocket.close()
        return

    mpd_text = receive_data(clientSocket) # from connectionSocket.sendall(mpd_data)
    print(mpd_text.decode())  

    bitrates = parse_bitrates(mpd_text)

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    chunk_num = 0
    bitrate = bitrates[0] # starting bitrate is always lowest

    tcurr = 0 # starting throughput should be 0

    while (True): #loop of .m4s files
        chunk_name = video_name + "_" + str(bitrate) + "_" + str(chunk_num).zfill(5)
        print(chunk_name)

        tstart = time.time() #start of request

        send_req(clientSocket, chunk_name)
        res = receive_msg(clientSocket)
        if res == "error: file not found" or res == "error: IO failed":
            clientSocket.close() #DC from server if not found
            break #last file

        curr_file = open(f"tmp/chunk_{chunk_num}.m4s", "wb")
        data = receive_data(clientSocket)

        tfin = time.time() # end of request

        curr_file.write(data)
        chunks_queue.put(f"tmp/chunk_{chunk_num}.m4s")
        chunk_num += 1
        
        tnew = calc_tnew(len(data), tstart, tfin)
        tcurr = update_tcurr(tcurr, alpha, tnew) # len(data) is the chunk size
        log_entry(time.time() - tnet_start, tstart, tfin, tnew, tcurr, bitrate, chunk_name)

        print(f"Tcurr: {tnew}, bitrate: {bitrate}")

        bitrate = update_bitrate(tcurr, bitrates)

    clientSocket.close()
    print("Client session termiated.")
    return

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
    # play_chunks(chunks_queue)
