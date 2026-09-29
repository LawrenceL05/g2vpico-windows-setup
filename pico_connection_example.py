import socket
from g2vpico import G2VPico

socket.setdefaulttimeout(20)
pico = G2VPico("169.254.84.67", "0000000031a0525e")
print("Channels:", pico.channel_count)
