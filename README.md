# CSEE 4119 Spring 2025, Assignment 1
## Sunny Carlin Qi
## GitHub username: SunnyQCU

*Please replace this text with information on how to run your code, description of each file in the directory, and any assumptions you have made for your code*

client.py:
    Currently successfully requests all 30 files and fill them
    into the tmp folder as requested. Also invalid video requests
    closes gracefully.

server.py:
    Currently successfully sends all 30 files to client as requested.
    Also invalid video requests closes gracefully.

TESTING.md:
    Contains four test cases. Specifically, the cases are: high alpha, low alpha, 
    wrong video name, and high latency.
    
Some assumptions:
    I've standardized the size of the file_size message to 64 bytes across
    the server and client. In other words, when receiving the message that
    indicates the file size of the chunk, the size of the message itself
    is expected to be 64 bytes (which have been zero padded)
