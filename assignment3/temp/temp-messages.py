import socket
import json
import time

HOST = "130.236.81.13";
PORT = 8716; 
my_unit_id = 4279;

def sock_setup():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((HOST, PORT))

    return sock;

def SendToHost(message):

    sock = sock_setup();
    sock.send("{}|".format(json.dumps(message)).encode()) 

    # getTasks list could be huge.
    receive = sock.recv(16384);
    
    sock.close();

    return json.loads(str(receive, 'utf-8').replace("|",""));

def GameListUnits():

    list_units_message = {"message_type":"GameListUnits","timeout":60}
    print(list_units_message)
    res = SendToHost(list_units_message);
    
    print(res);
    print(res["units"]);
    return;

def StartNewGame():

    game_control_message = {"game_state":"START","unit_id":my_unit_id,"message_type":"GameContol"}
    print(game_control_message)
    res = SendToHost(game_control_message)

    print(res)

    return;

def StopNewGame():

    game_control_message = {"game_state":"STOP","unit_id":my_unit_id,"message_type":"GameContol"}
    print(game_control_message)
    res = SendToHost(game_control_message)

    print(res)

    return;

def StopGame():

    game_control_message = {"game_state":"STOP","unit_id":my_unit_id,"message_type":"GameContol"}
    print(game_control_message)
    res = SendToHost(game_control_message)

    print(res)

    return;

def ledControl():

    msg = {
        "led_state":"OFF",
        "led_color":"RED",
        "from":my_unit_id,
        "message_type":
        "GameLEDControl",
        "to":my_unit_id
    }
    print(msg)
    res = SendToHost(msg)
    print(res)
    return;

def soundControl():

    sound_message = {
        "sound":"LOSE",
        "from":my_unit_id,
        "message_type":"GameSoundControl",
        "to":my_unit_id
    }
    print(sound_message)
    res = SendToHost(sound_message)
    print(res)

    return;

def GameGetTasks():

    get_task_message = {"unit_id":my_unit_id,"message_type":"GameGetTasks"}
    print(get_task_message)

    res = SendToHost(get_task_message)
    print(res)

    for task in res["tasks"]:

            match task["data"]["action"]:
                # propagate information to arduino using handler functions.
                case "PLAY_GAME":
                    print("-Game Control Task: " + task["data"]["game_state"])
                    print(str(task["from"]))
                    print()
                    
                case "CHANGE_LED": 
                    print("-Led Change Task: " + str(task["to"]))
                    print(task["data"]["led_color"])
                    print(task["data"]["led_state"])
                    print()
                
                case "PLAY_SOUND": 
                    print("-Sound Task: " + str(task["to"]))
                    print(task["data"]["sound"])
                    print()

                case "BUTTON_CHANGE":
                    print("-Button Change Task: " + str(task["to"]))
                    print("from: " + str(task["from"]))
                    print()


def GameRegister():

    game_register_message = {"unit_id":my_unit_id,"message_type":"GameRegister","registration_type":"register"}
    print(game_register_message);
    res = SendToHost(game_register_message);
    
    print(res)

    return;


# unregister the unit_id in the host
def GameUnregister():

    game_register_message = {"unit_id":my_unit_id,"message_type":"GameRegister","registration_type":"unregister"}
    print(game_register_message);
    res = SendToHost(game_register_message);
    
    print(res)

    return; 

def delay_call(func, staff):
    print(staff)
    time.sleep(2)
    func()

delay_call(GameRegister, "GameRegister")
delay_call(GameListUnits, "GameListUnits")
delay_call(StartNewGame, "StartNewGame")
delay_call(ledControl, "ledControl")
delay_call(soundControl, "soundControl")
delay_call(GameGetTasks, "GameGetTasks")
delay_call(StopGame, "StopGame")
delay_call(GameGetTasks, "GameGetTasks")
delay_call(GameUnregister, "GameUnregister")