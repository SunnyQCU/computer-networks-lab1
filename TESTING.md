# CSEE 4119 Spring 2025, Assignment 1 Testing File
## Sunny Carlin Qi
## GitHub username: SunnyQCU

*Please replace this text with test cases you have and results*

NOTE: For all test cases, I followed the procedure of starting network.py first, then
server.py, then finally client.py. 

Test case 1: (high alpha value)
    Bandwidth values:
        0:440000
        2:920000
        4:6000000
        6:1600000
        10:440000
    
    Below are the commands I ran in the different terminals in order:
        python3 network.py 50026 127.0.0.1 60026 ./bw.txt 0.1
        python3 server.py 60026
        python3 client.py 127.0.0.1 50026 bunny 0.9

    Alpha value: 0.9 (very reactive to changes)
    Latency: 0.1 (100ms, likely slower than average latency in real life)
    
    The reactive nature of a high alpha value was observed. For instance, between
    chunks 11 and 12, the Tcurr jumped from 1200519 to 2128300, and immediately the
    bitrate also jumped from 292312 to 612790, indicating that new throughput values 
    have a strong effect on bitrates. It also make sense in general for bitrate to
    increase as Tcurr increases.

Test Case 2: (wrong video requested)
    Bandwidth values:
        0:440000
        2:920000
        4:6000000
        6:1600000
        10:440000
    
    Below are the commands I ran in the different terminals in order:
        python3 network.py 50026 127.0.0.1 60026 ./bw.txt 0.5
        python3 server.py 60026
        python3 client.py 127.0.0.1 50026 bad_video 0.5

    Alpha value: 0.5
    Latency: 0.5

    This is the wrong video test case, and, as expected, right after
    the client sends out the request, and the server notifies the client
    that the video doesn't exists, it closes the connection and stops. Nothing
    is downloaded, and the program ran almost instantly (as there was no download).

Test case 3: (low alpha value)
    Bandwidth values:
        0:440000
        2:920000
        4:6000000
        6:1600000
        10:440000
    
    Below are the commands I ran in the different terminals in order:
        python3 network.py 50026 127.0.0.1 60026 ./bw.txt 0.05
        python3 server.py 60026
        python3 client.py 127.0.0.1 50026 bunny 0.1

    Alpha value: 0.1 (very slow to changes)
    Latency: 0.05 (50ms)
    
    With a low alpha value, the client saw a slow change in bitrate as well.
    For instance, chunk 14 had a throughput of 1913066, which would have been
    enough to result in a 987680 bitrate. However, since alpha was so low, the high
    value of chunk 14's throughput had little effect, resulting in a bitrate of 292312.

Test case 4: (high latency)
    Bandwidth values:
        0:440000
        2:920000
        4:6000000
        6:1600000
        10:440000
    
    Below are the commands I ran in the different terminals in order:
        python3 network.py 50026 127.0.0.1 60026 ./bw.txt 0.5
        python3 server.py 60026
        python3 client.py 127.0.0.1 50026 bunny 0.5

    Alpha value: 0.5
    Latency: 0.5 (500ms, very slow)
    
    As expected, with an extremely high latency, the video took a
    significantly long time to download (31 seconds). For reference, test case 3
    only took 8 seconds. Yet, it still fits well within the 60 second testing limit.


    