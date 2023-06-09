
import socket
import json
import time



#request = {"unit_id":4279,"message_type":"GameRegister","registration_type":"register"}
#request = {"unit_id":4279,"message_type":"GameGetTasks"}

#request = {"game_state":"START","unit_id":4278,"message_type":"GameContol"}
#request = {"game_state":"STOP","unit_id":4279,"message_type":"GameContol"}

#request = {"led_state":"ON","led_color":"AMBER","from":4279,"message_type":"GameLEDControl","to":4278}

#request = {"unit_id":4278,"message_type":"GameRegister","registration_type":"register"}
#request = {"unit_id":4278,"message_type":"GameGetTasks"}
#request = {"button_state":"PRESSED","from":4278,"message_type":"GameButtonControl","to":4279}

def sendToHost(request):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect(("130.236.81.13", 8716))

    print("{}|".format(json.dumps(request)).encode())
    sock.send("{}|".format(json.dumps(request)).encode())  

    receive = sock.recv(1024)
    sock.close()
    response = json.loads(str(receive,'utf-8').replace("|",""))

    print(response);


sendToHost({"unit_id":4279,"message_type":"GameRegister","registration_type":"unregister"})
sendToHost({"unit_id":4280,"message_type":"GameRegister","registration_type":"unregister"})
sendToHost({"unit_id":4281,"message_type":"GameRegister","registration_type":"unregister"})
time.sleep(0.5)
sendToHost({"message_type":"GameListUnits","timeout":60})