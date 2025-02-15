# CSEE 4119 Spring 2025, Assignment 1
## Sunny Carlin Qi
## GitHub username: SunnyQCU

*Please replace this text with information on how to run your code, description of each file in the directory, and any assumptions you have made for your code*

I believe we only edit client and serer, network and video_player should not be touched

To start server:
python3 server.py <listen_port>
i.e python3 server.py 60000 
(note, port can be between 49152-65535)
If you stop a server using ctrl+c, may take sometime before listening port is freed up again

To start client
python3 client.py <network_addr> <network_port> <name> <alpha>
i.e
    python3 client.py 127.0.0.1 50000 bunny 0.3