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

# TODO -- Simulate a full game ( just to see that what is sent is correct ) / use those functions
# TODO -- Create Multiplayer Script

import sys
import time
import socket
import threading
import serial
import json
import random

DEBUG_PRINT = True;

# DEFAULT ARGS
my_unit_id = 4279;
HOST = "130.236.81.13";
PORT = 8716; 
LOOP_DELAY = 2; 
MODE = "s"; # s singleplayer | m multiplayer

STATE_IDLE = "IDLE"
STATE_WAIT = "WAIT"
STATE_EXIT = "EXIT"

MODE_SINGLEPLAYER = "s";
MODE_MULTIPLAYER = "m";

LED_GREEN = "GREEN"
LED_RED = "RED"
LED_AMBER = "AMBER" 

LED_ON = "ON"
LED_OFF = "OFF"

BUTTON_PRESSED = "PRESSED"
BUTTON_RELEASED = "RELEASED"

SOUND_LOSE = "LOSE"
SOUND_WIN = "WIN"

# OTHER CONFIGURABLE ARGS
IDLE_TIMEOUT = 15
WAIT_TIMEOUT = 25
GAME_LOST_TIMEOUT = 5
GAME_WON_TIMEOUT = 2

EXIT_TIMEOUT = 15; # time to wait before exiting in order to let game master share sound and staff
SERIAL_CLOSE_TIMEOUT = 10;

# serial connection info
ser = None;

# The current state of the game
game_control = 0;
amber_state = LED_OFF;
game_master_id = None;
gstate = None;
gunits = None;
pressed = None;     # mark pressed/completed units
cunit_index = None; # the index of the unit we are waiting for click event
cred_index = None;  # the index of the button not to press

cOFFdict = {
    "GREEN": 2,
    "AMBER": 8,
    "RED"  : 32
}

cONdict = {
    "GREEN": 3,
    "AMBER": 12,
    "RED"  : 48
}

# block till data arrives
serial.Serial.timeout = None;

def debug_print(str):
    if(DEBUG_PRINT): print(" - DEBUG: " + str);

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
            case "-m":
                globals().update(MODE=int(sys.argv[entry + 1]))
            case _: 
                raise Exception("Argument Parsing Error");


# SPECIAL CASE: IF on STATE_IDLE and AMBER LIGHT is ON
# button press will set me as GAME MASTER and will START a new game.
def GameButtonPress(button_state):
    
    if (gstate == STATE_IDLE) and (amber_state == LED_ON):
        debug_print("Button Press when AMBER is ON")
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
# catch 1s and 0s, send GameButtonPresses if seen.
def gatewayLoop():
    debug_print("Gateway Active")
    while(True):
        # block here until 1 bytes arrives; see line 41
        # only check if byte is 1 or 0
        data = ser.read(1).decode()
        debug_print("G-Way: Got: " + data)

        if data == "1":
            GameButtonPress(BUTTON_PRESSED);
        elif data == "0":
            GameButtonPress(BUTTON_RELEASED);


# start a thread that will keep watch at arduino Serial
# for button presses and will send messages to host if needed be
def initGateway():
    th = threading.Thread(target=gatewayLoop, args=(1, ), daemon=True)
    th.start();
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
    th = threading.Thread(target=idle_loop, args=(1, ))
    th.start();

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
    debug_print("T_GM:Temporal Master Idle Loop Active");
    len_units = len(gunits)
    ledControl(gunits[0], LED_AMBER, LED_ON)
    next_index = 1;

    while(True):        
        for index in range(0, len_units - 1):
        
            if(gstate != STATE_IDLE): 
                break;    

            # sleep for some time then check if out of IDLE STATE
            for i in range(IDLE_TIMEOUT/3):
                time.sleep(IDLE_TIMEOUT/5)
                if(gstate != STATE_IDLE): 
                    break;
            
            debug_print("T_GM: Next index");

            next_index = index+1; 

            ledControl(gunits[index], LED_AMBER, LED_OFF)
            ledControl(gunits[next_index], LED_AMBER, LED_ON)
        
        GameListUnits(); # update your list for the next loop
        if(gstate != STATE_IDLE):
            break;
        debug_print("T_GM: Re-Looping");

    ledControl(gunits[next_index], LED_AMBER, LED_OFF)
    debug_print("T_GM:Temporal Master Idle Loop exit");
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

def soundControl(state, frm , to):

    sound_message = {
        "sound":state,
        "from":frm,
        "message_type":"GameSoundControl",
        "to":to
    }

    res = SendToHost(sound_message)
    success_check(res, "Sound Play Error")

    return;

# get a list of tasks for this unit
def GameGetTasks():

    get_task_message = {"unit_id":my_unit_id,"message_type":"GameGetTasks"}
    res = SendToHost(get_task_message)

    return res["tasks"]

def pospone_exit():
    debug_print("Pospone Exit thread Active")
    time.sleep(EXIT_TIMEOUT)
    gstate = STATE_EXIT;

def init_play_game():

    debug_print("Starting A New Game and Inacting Game Master")

    GameListUnits()
    debug_print("Updated List of Units")

    StartNewGame(); # propagate game start to all units connected 
    #gstate = STATE_WAIT;
    game_control = 1;
    random.shuffle(gunits) # get a random order
    debug_print("Game Unit Order " + gunits)

    pressed = [0] * len(gunits) # init an array that marks pressed units
    cunit_index = 0;
    th = threading.Thread(target=wait_state, args=(1, ))
    th.start();

def hanldePlayGame(task):

    debug_print("Got Game State: " + (task["data"]["game_state"]).upper())

    # SET game_master_id the from field.
    match((task["data"]["game_state"]).upper()):
        
        case "START":
            game_master_id = task["from"];
            debug_print("Set Game Master To unit_id: " + str(task["from"]))
            gstate = STATE_WAIT;
            if(game_master_id == my_unit_id):
                init_play_game()
        
        case "STOP": # entry exit state after some seconds.
            th = threading.Thread(target=pospone_exit, args=(1, ))
            th.start()
            return;


# send an n length message to the arduino using Serial
def sendToDevice(instruction):
    
    ba = bytearray([instruction])
    ser.write(ba)

    return;
    

def decodeLedInstruction(lcolor, lstate):

    if lstate == LED_OFF:
        return cOFFdict[lcolor];
    else:
        return cONdict[lcolor];


# IMPORTANT: KEEP TRACK OF AMBER LIGHT STATE ( needed for GameButtonPress )
def handleChangeLed(task):
    
    iid = random.randrange(1000, 100000)
    debug_print("Change Led Task for : " + str(task["to"])+ " | iid: " + str(iid) )

    # return if led action is not for this device
    if task["to"] != my_unit_id:
        return;

    debug_print("Change led COLOR: " + (task["data"]["led_color"]).upper()+ " | iid: " + str(iid) )
    debug_print("Change led STATE: " + (task["data"]["led_state"]).upper()+ " | iid: " + str(iid) )

    lcolor = (task["data"]["led_color"]).upper();
    lstate = (task["data"]["led_state"]).upper();
    
    # keep note of AMBER state
    if(lcolor == LED_AMBER):
        amber_state = lstate;

    instruction = decodeLedInstruction(lcolor, lstate);
        
    debug_print("Instruction to Device: " + str(instruction) + " | iid: " + str(iid) )
    
    sendToDevice(instruction)

    debug_print("Sent: " + str(instruction) + " | iid: " + str(iid) )

    
    return;


def handlePlaySound(task):
    
    iid = random.randrange(1000, 100000)
    debug_print("Play Sound Task for : " + str(task["to"])+ " | iid: " + str(iid) )

    if task["to"] != my_unit_id:
        return;

    debug_print("Play Sound: " + (task["data"]["sound"]).upper()+ " | iid: " + str(iid) )

    ins = 0;
    if (task["data"]["sound"]).upper() == SOUND_WIN:
        ins = 192;
    else:
        ins = 128;

    sendToDevice(ins)
    debug_print("Sent: " + str(ins) + " | iid: " + str(iid) )


# __ONLY__ WHEN UNIT IS THE GAME MASTER
# send pulsing green for 8 secs 
def game_won():

    debug_print("GM: Initiating Game Won Sequence")


    for u in gunits:
        soundControl(SOUND_WIN, my_unit_id, u)
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
def game_lost():

    debug_print("GM: Initiating Game Lost Sequence")

    for u in gunits:
        soundControl(SOUND_LOSE, my_unit_id, u)
        ledControl(u, LED_RED, LED_ON)
    
    time.sleep(GAME_LOST_TIMEOUT)

    for u in gunits:
        ledControl(u, LED_RED, LED_OFF)

    return;

# __ONLY__ WHEN UNIT IS THE GAME MASTER
# pick a random unit to be red
def handle_red(fid):

    cred_index = 9090; # default red index, handles a specific condition

    # do not draw random unit for red if all units except one are pressed
    if not (len(gunits) - sum(pressed) == 1): 
        cred_index = random.randrange(len(gunits))
    
        while(cunit_index == cred_index):
            cred_index = random.randrange(len(gunits))

        ledControl(gunits[cred_index], LED_RED, LED_ON)
    else:
        debug_print("GM: No Red Unit Pick. Using Default." + " | fid: " + str(fid))
    return;

# __ONLY__ WHEN UNIT IS THE GAME MASTER 
# pick the next cunit_index as yellow, pick a random unit as red ( if exists )
# send appropriate light up signals, sleep for WAIT_TIMEOUT seconds
# when woken up check if pressed array is marked. If not, lose and 
# go to exit state. 
def wait_state():
    
    # next unit
    cunit_index = (cunit_index + 1)%len(gunits)
    
    # debug staff
    fid = random.randrange(1000, 100000);
    debug_print("GM: In wait_state | fid: " + str(fid))

    # copy to a local index in order to be sure that cunit_index will be the same after timeout
    local_index_copy = cunit_index; 

    debug_print("GM: AMBER unit index: " + str(local_index_copy) + " | fid: " + str(fid))

    if pressed[local_index_copy]:
        game_won(); # do winning staff 
        StopGame()
        return;

    ledControl(gunits[local_index_copy], LED_AMBER, LED_ON)

    handle_red(fid);
    
    debug_print("GM: RED unit index: " + str(cred_index) + " | fid: " + str(fid))

    time.sleep(WAIT_TIMEOUT)

    if not pressed[local_index_copy]:
    
        debug_print("GM: Correct Unit Index not pressed, Game Over." + " | fid: " + str(fid))
    
        game_lost()
        StopGame()

# __ONLY__ WHEN UNIT IS THE GAME MASTER 
# light cunit_index GREEN, close red and amber lighs. 
# Mark pressed and init the wait_state thread.
def CorrectButtonPress():

    pressed[cunit_index] = 1;
    ledControl(gunits[cunit_index], LED_GREEN, LED_ON)

    # close wait state lighrs
    ledControl(gunits[cunit_index], LED_AMBER, LED_OFF)
    ledControl(gunits[cred_index], LED_RED, LED_OFF)

    th = threading.Thread(target=wait_state, args=(1, ))
    th.start()

    return;

# __ONLY__ WHEN UNIT IS THE GAME MASTER 
# lose and go to EXIT state
def WrongButtonPress():

    # close wait state lighrs
    ledControl(gunits[cunit_index], LED_AMBER, LED_OFF)
    ledControl(gunits[cred_index], LED_RED, LED_OFF)

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

    # do not process button clicks if game state is not WAIT
    if(gstate != STATE_WAIT):
        return;

    # loop through all button messages.
    for action in actions: 

        if(action["data"]["button_state"] != "PRESSED"):

            if MODE == MODE_SINGLEPLAYER:
                debug_print("GM: Ignoring RELEASED PRESS from:" + str(action["from"]))

            else:
                debug_print("GM: Got RELEASED from :" + str(action["from"]))
            
                # if button is logged as pressed, lose_game 
                if(pressed[action["from"]]):
                    debug_print("GM: from : " + str(action["from"]) + " button was active and now it was released. ")
                    WrongButtonPress()
                    break; # do not process next actions as game is lost
            continue;

        # skip if for some reason this button action does not involve you
        if action["to"] != my_unit_id: continue;

        if action["from"] == gunits[cunit_index]:
            debug_print("GM: Correct Button Press from :" + str(action["from"]))
            CorrectButtonPress();
        
        elif action["from"] == gunits[cred_index]:
            debug_print("GM: InCorrect Button Press from :" + str(action["from"]))
            debug_print("GM: Expected Button Press from :" + str(gunits[cred_index]))
            WrongButtonPress();
                


    return;

# handle available tasks / filter button events if needed.
# return a list of required actions
# loop through all tasks
def GameHandleTasks(tasks):

    actions = []

    for task in tasks:
        debug_print("Received New Task")
        debug_print("Processing: " + task["data"]["action"])
        match task["data"]["action"]:
            # propagate information to arduino using handler functions.
            case "PLAY_GAME": hanldePlayGame(task);

            case "CHANGE_LED": handleChangeLed(task);
            case "PLAY_SOUND": handlePlaySound(task);

            # append Button actions and process only if you are game master
            case "BUTTON_CHANGE": actions.append(task);
    
    return actions;

def my_unit_exit():
    ledControl(my_unit_id, LED_AMBER, LED_OFF)
    ledControl(my_unit_id, LED_RED, LED_OFF)
    ledControl(my_unit_id, LED_GREEN, LED_OFF)
    GameUnregister();
    time.sleep(SERIAL_CLOSE_TIMEOUT);
    ser.close();


# ENTRY POINT
def main():
    ser = serial.Serial('/dev/ttyACM0',9600)
    parse_argv();
    debug_print("Parsed Arguments");
    initGateway();
    debug_print("Gateway Initialized");
    
    try:
        GameRegister()
        debug_print("Registered to Game");

        GameListUnits()
        debug_print("Got Initial Unit List");

        gstate = STATE_IDLE;
        if(onlyMeRegistered()):
            debug_print("T_GM: Inacting Temporal Master");
            init_temporal()

    except (KeyboardInterrupt, SystemExit, Exception) as err:
        debug_print("ERROR: Initialization Error:")
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
            debug_print("ERROR: Gameplay Error:")
            # unregister before exit
            my_unit_exit();
            if not isinstance(err, (KeyboardInterrupt, SystemExit)):
                print(err);
            exit(-1);

        time.sleep(LOOP_DELAY);
    
    debug_print("Unit Exit")
    my_unit_exit();

if __name__ == '__main__':
    debug_print('Game Start | Active Game Logic : ' + MODE);  
    main();
