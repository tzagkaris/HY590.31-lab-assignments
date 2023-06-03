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

# DEFAULT ARGS
unit_id = 4279;
HOST = "130.236.81.13";
PORT = 8716;
GAME_CONTROL = 0; 
LOOP_DELAY = 2; 


STATE_IDLE = "IDLE"
STATE_WAIT = "WAIT"

LED_GREEN = "GREEN"
LED_RED = "RED"
LED_AMBER = "AMBER"

LED_ON = "ON"
LED_OFF = "OFF"

# OTHER CONFIGURABLE ARGS
IDLE_TIMEOUT = 15
WAIT_TIMEOUT = 25
GAME_LOST_TIMEOUT = 5
GAME_WON_TIMEOUT = 2

# The current state of the game
gstate = None;
gunits = None;
pressed = None;     # mark pressed/completed units
cunit_index = None; # the index of the unit we are waiting for click event
cred_index = None;  # the index of the button not to press

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
    pressed = len(gunits) * [0];
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

def ledControl(unit, color, state):

    msg = {
        "led_state":state,
        "led_color":color,
        "from":unit_id,
        "message_type":
        "GameLEDControl",
        "to":unit
    }

    SendToHost(msg)
    return;
    

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# loop for init_idle. Loops through all units and sends an AMBER message to the 
# current unit. After 15 secs, will move to the next unit, shutting down the prev one.
# stop looping and end thread exec when gstate != STATE_IDLE
def idle_loop():    
    
    len_units = len(gunits)
    unit_index = 0;

    ledControl(gunits[unit_index], LED_AMBER, LED_ON)

    while(gstate == STATE_IDLE):
        
        time.sleep(IDLE_TIMEOUT)
        last_index = unit_index;
        unit_index = (unit_index + 1)%len_units; 
        
        cunit_index = unit_index;

        ledControl(gunits[last_index], LED_AMBER, LED_OFF)
        ledControl(gunits[unit_index], LED_AMBER, LED_ON)

    ledControl(gunits[unit_index], LED_AMBER, LED_OFF)

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

    game_register_message = {"unit_id":unit_id,"message_type":"GameRegister","registration_type":"unregister"}
    res = SendToHost(game_register_message);
    
    success_check(res, "Game UnRegister Error!")

    return;

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

def game_won():
    
    for u in gunits:
        ledControl(u, LED_GREEN, LED_ON)
    
    time.sleep(GAME_WON_TIMEOUT)

    for u in gunits:
        ledControl(u, LED_GREEN, LED_OFF)

    time.sleep(GAME_WON_TIMEOUT)

    for u in gunits:
        ledControl(u, LED_GREEN, LED_ON)

    time.sleep(GAME_WON_TIMEOUT)

    for u in gunits:
        ledControl(u, LED_GREEN, LED_OFF)

    time.sleep(GAME_WON_TIMEOUT)


    pass;

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# send led red to all units for 5 secs.
# TODO, add sound instructions
def game_lost():

    for u in gunits:
        ledControl(u, LED_RED, LED_ON)
    
    time.sleep(GAME_LOST_TIMEOUT)

    for u in gunits:
        ledControl(u, LED_RED, LED_OFF)

    return;

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# pick the next cunit_index as yellow, pick a random unit as red
# send appropriate signals, sleep for WAIT_TIMEOUT seconds
# when woken up, close red and yellow leds and
# if pressed array is not marked lose and 
# go to IDLE state ( if not already in IDLE state ) | init idle_loop. 
#
# TODO, add sound instructions for correct press
def wait_state():
    
    cunit_index = (cunit_index + 1)%len(gunits)
    if(pressed[cunit_index]):
        game_won(); # do staff 
        if gstate != STATE_IDLE: # WrongButtonPress might have already changed the state to idle
            init_idle();
        return;

    cred_index = random.randrange(len(gunits))
    
    while(cunit_index == cred_index):
        cred_index = random.randrange(len(gunits))

    ledControl(gunits[cunit_index], LED_AMBER, LED_ON)
    ledControl(gunits[cred_index], LED_RED, LED_ON)

    time.sleep(WAIT_TIMEOUT)

    ledControl(gunits[cunit_index], LED_AMBER, LED_OFF)
    ledControl(gunits[cred_index], LED_RED, LED_OFF)

    if not pressed[cunit_index]:
        game_lost()
        if gstate != STATE_IDLE: # WrongButtonPress might have already changed the state to idle
            init_idle();

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# light cunit_index GREEN, mark pressed and init the wait_state thread.
def CorrectButtonPress():

    pressed[cunit_index] = 1;
    ledControl(gunits[cunit_index], LED_GREEN, LED_ON)
    threading.Thread(target=wait_state, args=(1, ))

    return;

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# lose and go to IDLE state (if not already in IDLE state ) | init idle_loop.
def WrongButtonPress():

    game_lost(); # send led red to all units for 5 secs.
    if gstate != STATE_IDLE: # wait state might have already changed the state to idle
        init_idle();

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# if on IDLE state | check "from" field | if "from" is the same as gunits[cunit_index] then 
# go to wait state and init the wait_state thread.
# 
# if on WAIT state | check "from" field | 
# if "from" is the same as gunits[cunit_index] then
# light GREEN, mark pressed and init the wait_state thread.
# ELSE
# if "from" is the same as the unit we switched led RED then
# lose and go to IDLE state (if not already ) | init idle_loop.
def handleGameButtonPress(actions):

    # loop through all button messages.
    for action in actions: 

        # skip if for some reason this button action does not involve you
        if action["to"] != unit_id: continue;

        match gstate: 
            case "IDLE":
                if action["from"] == gunits[cunit_index]:
                    threading.Thread(target=wait_state, args=(1, ))

            case "WAIT":
                if action["from"] == gunits[cunit_index]:
                    CorrectButtonPress();

                elif action["from"] == gunits[cred_index]:
                    WrongButtonPress();
                
                # else continue
        time.sleep(1)


    return;

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

            # append Button actions and process only if you are game master
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
    except (KeyboardInterrupt, SystemExit, Exception) as err:
        print("Initialization Error:")
        GameUnregister()
        if not isinstance(err, (KeyboardInterrupt, SystemExit)):
            print(err);
        exit(-1);
    
    # MAIN LOOP
    while(True):
        try:
            tasks = GameGetTasks()
            actions = GameHandleTasks(tasks)
            if GAME_CONTROL:
                handleGameButtonPress(actions)
        
        except (KeyboardInterrupt, SystemExit, Exception) as err:
            # unregister before exit
            GameUnregister()
            if not isinstance(err, (KeyboardInterrupt, SystemExit)):
                print(err);
            exit(-1);

        time.sleep(LOOP_DELAY);
                    

if __name__ == '__main__':    
    main();
