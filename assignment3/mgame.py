# LAB 3 GAME SCRIPT
# CSD 4279 - CSDP **** - CSDP ****
# 
# 
# USAGE:
# python3 mgame.py [ argv ]
#   argv
#   -h HOST
#   -p PORT
#   -u unit_id ( integer )
#   -G Game Control ( 1 | 0 )
#   -t loop_timeout seconds ( integer > 1 )

import sys
import time
import socket
import threading
import serial
import json
import random
import copy

# DEFAULT ARGS
unit_id = 4279;
HOST = "130.236.81.13";
PORT = 8716;
GAME_CONTROL = 0; 
LOOP_DELAY = 2; 

# OTHER CONFIGURABLE ARGS
STATE_IDLE = "IDLE"
IDLE_TIMEOUT = 15


# The current state of the game
gstate = None;
gunits = None;
cunit_index = None; # the index of the unit we are waiting for click event.

# block till data arrives
serial.Serial.timeout = None;

# overwrite arguments
def parse_argv():
    args_no = len(sys.argv)
    
    entry = 1;
    for entry in range(1,args_no):
        
        if(entry%2 == 0): continue;

        match sys.argv[entry]:
            case "-h": 
                globals().update(HOST=sys.argv[entry + 1])
            case "-p": 
                globals().update(PORT=int(sys.argv[entry + 1]))
            case "-u": 
                globals().update(unit_id=int(sys.argv[entry + 1]))
            case "-G":
                globals().update(GAME_CONTROL=int(sys.argv[entry + 1]))
            case "-d":
                globals().update(LOOP_DELAY=int(sys.argv[entry + 1]))            
            case _: 
                raise Exception("Argument Parsing Error");

def GameButtonPress():
    pass;

# connect to Serial and loop till data arrives
# if data is **** then call GameButtonPress
def gatewayLoop():
    
    ser = serial.Serial('/dev/ttyACM0',9600)

    while(True):
        # block here until 4 bytes arrive; see line 41
        data = ser.read(4).decode("utf-8")
        # TODO fill this with Vaggos
        
        #if(True):
        #    GameButtonPress()

# start a thread that will keep watch at arduino Serial
# for button presses and will send messages to host if needed be
def initGateway():
    threading.Thread(target=gatewayLoop, args=(1, ), daemon=True)
    return;

def sock_setup():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((HOST, PORT))

    return sock;

def SendToHost(message):

    sock = sock_setup();
    sock.send("{}|".format(json.dumps(message)).encode()) 

    # getTasks list could could be huge.
    receive = sock.recv(16384);
    
    sock.close();

    return json.loads(str(receive, 'utf-8').replace("|",""));

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# get Unit Lists 
def GameListUnits():

    list_units_message = {"message_type":"GameListUnits","timeout":60}
    res = SendToHost(list_units_message);
    
    gunits = res["units"];
    return;

# check if response was successful
def success_check(response, er_msg):
    if(response["success"] != "True"):
        raise Exception(er_msg, response);
    return;

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# start a new game, 
# define order and sent appropriate StartControl message.
def StartNewGame():

    random.shuffle(gunits)

    game_control_message = {"game_state":"START","unit_id":unit_id,"message_type":"GameContol"}
    res = SendToHost(game_control_message)

    success_check(res, "Game Control-Start Game- Error!")

    gstate = STATE_IDLE;
    return;

# loop for init_idle. Loops through all units and sends an AMBER message to the 
# current unit. After 15 secs, will move to the next unit, shutting down the prev one.
# stop looping and end thread exec when gstate != STATE_IDLE
def idle_loop():    
    
    len_units = len(gunits)
    unit_index = 0;

    light_up_message = {
        "led_state":"ON",
        "led_color":"AMBER",
        "from":unit_id,
        "message_type":
        "GameLEDControl",
        "to":gunits[unit_index]
    }
    
    light_down_message = {
        "led_state":"OFF",
        "led_color":"AMBER",
        "from":unit_id,
        "message_type":"GameLEDControl",
        "to":gunits[unit_index]
    }

    SendToHost(copy.deepcopy(light_up_message));

    while(gstate == STATE_IDLE):
        
        time.sleep(IDLE_TIMEOUT)
        last_index = unit_index;
        unit_index = (unit_index + 1)%len_units; 
        
        cunit_index = unit_index;

        tldm = copy.deepcopy(light_down_message)
        tlum = copy.deepcopy(light_up_message)

        tldm["to"] = gunits[last_index];
        SendToHost(tldm)
        tlum["to"] = gunits[unit_index];
        SendToHost(tlum)

    light_down_copy = copy.deepcopy(light_down_message)
    light_down_copy["to"] = gunits[unit_index];
    
    SendToHost(light_down_copy)
    return;

# start a thread to handle idle state
def init_idle():
    threading.Thread(target=idle_loop, args=(1, ))
    return;

# register the unit_id in the host
def GameRegister():

    game_register_message = {"unit_id":unit_id,"message_type":"GameRegister","registration_type":"register"}
    res = SendToHost(game_register_message);
    
    success_check(res, "Game Register Error!")

    return;


# unregister the unit_id in the host
def GameUnregister():
    pass;

# get a list of tasks for this unit
def GameGetTasks():

    get_task_message = {"unit_id":unit_id,"message_type":"GameGetTasks"}
    res = SendToHost(get_task_message)

    return res["tasks"]

# send an n length message to the arduino using serial
def sendToDevice(string_message):
    pass;

def hanldePlayGame():
    pass;

def handleChangeLed():
    pass;

def handlePlaySound():
    pass;

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
def handleGameButtonPress(actions):
    pass;

# handle available tasks / filter button events if needed.
# return a list of required actions
# loop through all tasks
#   if task is GameLedControl call for your unit id - call handler function
#   if task is GameControl (start / stop ) - call handler function
#   if task is GameSoundControl - call handler function
#   
#   if task is GameButtonControl - add it to returned actions list
def GameHandleTasks(tasks):

    actions = []

    for task in tasks:
        match task["data"]["action"]:
            # propagate information to arduino using handler functions.
            case "PLAY_GAME": hanldePlayGame(task);
            case "CHANGE_LED": handleChangeLed(task);
            case "PLAY_SOUND": handlePlaySound(task);

            # handle this only when you are game master
            case "BUTTON_CHANGE": actions.append(task);
    

    return actions;


# ENTRY POINT
def main():
    parse_argv();    
    initGateway();
    
    try:
        GameRegister();
        if GAME_CONTROL:
            GameListUnits() 
            StartNewGame()
            init_idle()
    except Exception as err:
        print("Initialization Error:")
        print(err)
        exit(-1);
    
    # MAIN LOOP
    while(True):
        try:
            tasks = GameGetTasks()
            actions = GameHandleTasks(tasks)
            if GAME_CONTROL:
                handleGameButtonPress(actions)
        
        except Exception as err:
            # what should be done when error happens ? ?
            print("Game Loop Error:")
            print(err);

        time.sleep(LOOP_DELAY);

    #GameUnregister()
                    

if __name__ == '__main__':    
    main();
