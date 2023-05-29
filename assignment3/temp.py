
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.connect(("130.236.81.13", 8716))

request = {"unit_id":4279,"message_type":"GameRegister","registration_type":"unregister"}
print("{}|".format(json.dumps(request)).encode())
sock.send("{}|".format(json.dumps(request)).encode())    
receive = sock.recv(1024)
sock.close()
response = json.loads(str(receive,'utf-8').replace("|",""))
print(response);