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
my_unit_id = 4279;
HOST = "130.236.81.13";
PORT = 8716; 
LOOP_DELAY = 2; 

STATE_IDLE = "IDLE"
STATE_WAIT = "WAIT"
STATE_EXIT = "EXIT"

LED_GREEN = "GREEN"
LED_RED = "RED"
LED_AMBER = "AMBER" 

LED_ON = "ON"
LED_OFF = "OFF"

BUTTON_PRESSED = "PRESSED"
BUTTON_RELEASED = "RELEASED"

AMBER_ON = 1;
AMBER_OFF = 0;

# OTHER CONFIGURABLE ARGS
IDLE_TIMEOUT = 15
WAIT_TIMEOUT = 25
GAME_LOST_TIMEOUT = 5
GAME_WON_TIMEOUT = 2

EXIT_TIMEOUT = 15; # time to wait before exiting in order to let game master share sound and staff

# The current state of the game
game_control = 0;
amber_state = AMBER_OFF;
game_master_id = None;
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
                globals().update(my_unit_id=int(sys.argv[entry + 1]))
            case "-d":
                globals().update(LOOP_DELAY=int(sys.argv[entry + 1]))            
            case _: 
                raise Exception("Argument Parsing Error");


# SPECIAL CASE: IF on STATE_IDLE and AMBER LIGHT is ON
# button press will set me as GAME MASTER and will START a new game.
# TODO, send button press to game master
def GameButtonPress(button_state):
    
    if (gstate == STATE_IDLE) and (amber_state == AMBER_ON):
        StartNewGame()
        return;

    button_update_message = {
        "button_state":button_state,
        "from":my_unit_id,
        "message_type":"GameButtonControl",
        "to":game_master_id
    }

    res = SendToHost(button_update_message)
    success_check(res, "Button Press to Host Error!")
    return;

# connect to Serial and loop till data arrives
# if data is **** then call GameButtonPress ( singleplayer logic )
# TODO, figure this out with team 
def gatewayLoop():
    
    ser = serial.Serial('/dev/ttyACM0',9600)

    while(True):
        # block here until 4 bytes arrive; see line 41
        data = ser.read(4).decode("utf-8")
        # TODO fill this with Vaggos
        
        #if(True):
        #    GameButtonPress(BUTTON_PRESSED)

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

    # getTasks list could be huge.
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

def onlyMeRegistered():

    if(len(gunits) == 1):
        return True;

    return False;

def init_temporal():
    threading.Thread(target=idle_loop, args=(1, ))

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# start a new game, 
# define order and sent appropriate StartControl message.
def StartNewGame():

    random.shuffle(gunits)

    game_control_message = {"game_state":"START","unit_id":my_unit_id,"message_type":"GameContol"}
    res = SendToHost(game_control_message)

    success_check(res, "Game Control-Start Game- Error!")

    return;

def StopGame():

    game_control_message = {"game_state":"STOP","unit_id":my_unit_id,"message_type":"GameContol"}
    res = SendToHost(game_control_message)

    success_check(res, "Game Control-Stop Game- Error!")

    return;

def ledControl(unit, color, state):

    msg = {
        "led_state":state,
        "led_color":color,
        "from":my_unit_id,
        "message_type":
        "GameLEDControl",
        "to":unit
    }

    SendToHost(msg)
    return;
    

# ONLY IF YOU ARE THE TEMPORAL MASTER 
# loop for init_idle. Loops through all units and sends an AMBER message to the 
# current unit. After 15 secs, will move to the next unit, shutting down the prev one.
# stop looping and end thread exec when gstate != STATE_IDLE
def idle_loop():    
    
    
    len_units = len(gunits)
    ledControl(gunits[0], LED_AMBER, LED_ON)
    next_index = 1;

    while(True):
        for index in range(0, len_units - 1):
        
            if(gstate != STATE_IDLE): 
                break;    
        
            time.sleep(IDLE_TIMEOUT)

            next_index = index+1; 

            ledControl(gunits[index], LED_AMBER, LED_OFF)
            ledControl(gunits[next_index], LED_AMBER, LED_ON)
        
        GameListUnits(); # update your list for the next loop
        if(gstate != STATE_IDLE):
            break;
    
    ledControl(gunits[next_index], LED_AMBER, LED_OFF)

    return;

# register the unit_id in the host
def GameRegister():

    game_register_message = {"unit_id":my_unit_id,"message_type":"GameRegister","registration_type":"register"}
    res = SendToHost(game_register_message);
    
    success_check(res, "Game Register Error!")

    return;


# unregister the unit_id in the host
def GameUnregister():

    game_register_message = {"unit_id":my_unit_id,"message_type":"GameRegister","registration_type":"unregister"}
    res = SendToHost(game_register_message);
    
    success_check(res, "Game UnRegister Error!")

    return;

# get a list of tasks for this unit
def GameGetTasks():

    get_task_message = {"unit_id":my_unit_id,"message_type":"GameGetTasks"}
    res = SendToHost(get_task_message)

    return res["tasks"]

def pospone_exit():
    time.sleep(EXIT_TIMEOUT)
    gstate = STATE_EXIT;

def init_play_game():

    GameListUnits()
    StartNewGame(); # propagate game start to all units connected 
    gstate = STATE_WAIT;
    game_control = 1;
    random.shuffle(gunits) # get a random order
    pressed = [0] * len(gunits) # init an array that marks pressed units
    cunit_index = 0;
    threading.Thread(target=wait_state, args=(1, ))


def hanldePlayGame(task):
    # SET game_master_id the from field.
    match(task["data"]["game_state"]):
        
        case "START":
            game_master_id = task["from"];
            if(game_master_id == my_unit_id):
                init_play_game()
        
        case "STOP": # entry exit state after some seconds.
            threading.Thread(target=pospone_exit, args=(1, ))
            return;


# send an n length message to the arduino using Serial
# TODO
def sendToDevice(string_message):
    pass;

# TODO, decode led request and propagate to arduino, call sendToDevice
# IMPORTANT: KEEP TRACK OF AMBER LIGHT STATE ( needed for GameButtonPress )
def handleChangeLed():
    pass;

# TODO, decode sound request and propagate to arduino, call sendToDevice
def handlePlaySound():
    pass;

# __ONLY__ WHEN UNIT IS THE GAME MASTER
# send pulsing green for 8 secs 
# TODO, add sound instructions
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

# __ONLY__ WHEN UNIT IS THE GAME MASTER
# send led red to all units for 5 secs.
# TODO, add sound instructions
def game_lost():

    for u in gunits:
        ledControl(u, LED_RED, LED_ON)
    
    time.sleep(GAME_LOST_TIMEOUT)

    for u in gunits:
        ledControl(u, LED_RED, LED_OFF)

    return;

# __ONLY__ WHEN UNIT IS THE GAME MASTER
# pick a random unit to be red
def handle_red():
    # do not draw random unit for red if all units except one are pressed
    if not (len(gunits) - sum(pressed) == 1): 
        cred_index = random.randrange(len(gunits))
    
        while(cunit_index == cred_index):
            cred_index = random.randrange(len(gunits))

        ledControl(gunits[cred_index], LED_RED, LED_ON)
    
    return;

# __ONLY__ WHEN UNIT IS THE GAME MASTER 
# pick the next cunit_index as yellow, pick a random unit as red ( if exists )
# send appropriate light up signals, sleep for WAIT_TIMEOUT seconds
# when woken up check if pressed array is marked. If not, lose and 
# go to exit state. 
def wait_state():
    
    # next unit
    cunit_index = (cunit_index + 1)%len(gunits)

    if(pressed[cunit_index]):
        game_won(); # do winning staff 
        StopGame()
        return; 

    ledControl(gunits[cunit_index], LED_AMBER, LED_ON)

    handle_red();

    time.sleep(WAIT_TIMEOUT)

    if not pressed[cunit_index]:
        game_lost()
        StopGame()

# __ONLY__ WHEN UNIT IS THE GAME MASTER 
# light cunit_index GREEN, close red and amber lighs. 
# Mark pressed and init the wait_state thread.
def CorrectButtonPress():

    pressed[cunit_index] = 1;
    ledControl(gunits[cunit_index], LED_GREEN, LED_ON)

    ledControl(gunits[cunit_index], LED_AMBER, LED_OFF)
    ledControl(gunits[cred_index], LED_RED, LED_OFF)

    threading.Thread(target=wait_state, args=(1, ))

    return;

# __ONLY__ WHEN UNIT IS THE GAME MASTER 
# lose and go to EXIT state
def WrongButtonPress():
    game_lost()
    StopGame()

# __ONLY__ WHEN UNIT IS THE GAME MASTER
# check "from" field | 
# if "from" is the same as gunits[cunit_index] then
# light GREEN, mark pressed and init the wait_state thread.
# ELSE
# if "from" is the same as the unit we switched led RED then
# lose and go to IDLE state (if not already ) | init idle_loop.
def handleGameButtonPress(actions):

    # loop through all button messages.
    for action in actions: 

        # singleplayer logic
        # only accept button state == PRESSED
        # ignore button state == RELEASED
        if(action["data"]["button_state"] != "PRESSED"):
            continue;

        # skip if for some reason this button action does not involve you
        if action["to"] != my_unit_id: continue;

        if action["from"] == gunits[cunit_index]:
            CorrectButtonPress();
        elif action["from"] == gunits[cred_index]:
            WrongButtonPress();
                


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

def my_unit_exit():
    GameUnregister();
    
    ledControl(my_unit_id, LED_AMBER, LED_OFF)
    ledControl(my_unit_id, LED_RED, LED_OFF)
    ledControl(my_unit_id, LED_GREEN, LED_OFF)


# ENTRY POINT
def main():
    parse_argv();    
    initGateway();
    
    try:
        GameRegister()
        GameListUnits() 
        gstate = STATE_IDLE;
        if(onlyMeRegistered()):
            init_temporal()

    except (KeyboardInterrupt, SystemExit, Exception) as err:
        print("Initialization Error:")
        my_unit_exit();
        if not isinstance(err, (KeyboardInterrupt, SystemExit)):
            print(err);
        exit(-1);
    
    # MAIN LOOP
    while(True):
        try:
            tasks = GameGetTasks()
            actions = GameHandleTasks(tasks)
            if game_control:
                handleGameButtonPress(actions)

            if gstate == STATE_EXIT:
                break;
        
        except (KeyboardInterrupt, SystemExit, Exception) as err:
            print("Gameplay Error:")
            # unregister before exit
            my_unit_exit();
            if not isinstance(err, (KeyboardInterrupt, SystemExit)):
                print(err);
            exit(-1);

        time.sleep(LOOP_DELAY);
    
    my_unit_exit();
    print("Normal Exit. Bye!");

if __name__ == '__main__':    
    main();
