import socket
import json

id = 0 # Todo: Set your three digits from your LiU-ID here.
host = '130.236.81.13'
port = 8718

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.connect((host, port))

print(sock)


request = {
    "message_type":"TNK116SetThreshold",
    "id":id,
    "type": "humidity",
    "value": 22,
}

req_json = json.dumps(request);
req_bytes = (req_json + "|").encode("utf-8");

sock.send(req_bytes);

data = sock.recv(1024)
data = data.decode();
data = data[:-1];
rec = json.loads(data);
print(rec)


