"""Read device information without changing illumination."""
import argparse
import socket
from g2vpico import G2VPico


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ip", required=True, help="Pico wired IPv4 address")
    parser.add_argument("--id", required=True, help="16-character Pico ID")
    args = parser.parse_args()
    if len(args.id) != 16:
        parser.error("Pico ID must contain 16 characters, including leading zeros.")
    socket.setdefaulttimeout(10)
    try:
        pico = G2VPico(args.ip, args.id)
        print("Connected successfully")
        print("Pico ID:", pico.id)
        print("Channel count:", pico.channel_count)
        print("Available channels:", pico.channel_list)
    except Exception as exc:
        parser.exit(1, f"Connection failed: {exc}\n")


if __name__ == "__main__":
    main()
