import socket
import requests
import threading
import time

HOST = "blindmasters.org"
PORT = 10222

USERNAME = "plus"
PASSWORD = ""

NICKNAME = "TTIpChecker"
CLIENTNAME = "TTIpChecker v0.1 alfa"

def get_ip_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = r.json()
        return data.get("country", "Unknown"), data.get("isp", "Unknown")
    except:
        return "Unknown", "Unknown"

def send(cmd):
    try:
        s.send((cmd + "\r\n").encode("utf-8"))
        print(">>", cmd)
    except:
        print("Send error")

def keepalive():
    while True:
        send("ping")
        time.sleep(15)

# connect
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.settimeout(0.2)

print("Connected to TeamTalk5 server")

# LOGIN (nickname + clientname)
send(f'login username="{USERNAME}" password="{PASSWORD}" nickname="{NICKNAME}" clientname="{CLIENTNAME}"')

users_seen = set()

# keep connection alive
threading.Thread(target=keepalive, daemon=True).start()

buffer = ""

while True:

    try:
        data = s.recv(4096).decode("utf-8", errors="ignore")
        buffer += data
    except socket.timeout:
        continue
    except:
        print("Disconnected")
        break

    while "\n" in buffer:

        line, buffer = buffer.split("\n", 1)
        line = line.strip()

        if line.startswith("adduser"):

            parts = {}

            for item in line.split():
                if "=" in item:
                    k, v = item.split("=", 1)
                    parts[k] = v.strip('"')

            userid = parts.get("userid")

            if userid and userid not in users_seen:

                users_seen.add(userid)

                nickname = parts.get("nickname", "unknown")
                ip = parts.get("ipaddr", "0.0.0.0")
                version = parts.get("version", "unknown")

                country, isp = get_ip_info(ip)

                msg = (
                    f"New user | "
                    f"Nick: {nickname} | "
                    f"IP: {ip} | "
                    f"Country: {country} | "
                    f"Provider: {isp} | "
                    f"Client: {version}"
                )

                send(f'message type=3 content="{msg}"')

                print("Broadcast:", msg)