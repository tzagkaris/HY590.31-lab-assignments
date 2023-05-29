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

# DEFAULT ARGS
unit_id = 4279;
HOST = "130.236.81.13";
PORT = 8716;
GAME_CONTROL = 0; 
LOOP_DELAY = 2; 

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

# connect to Serial and loop till data arrives
# if data is **** then call GameButtonPress
def gatewayLoop():
    
    ser = serial.Serial('/dev/ttyACM0',9600)

    while(True):
        # block here until 4 bytes arrive;
        data = ser.read(4).decode("utf-8")
        # TODO fill this with Vaggos
        
        #if(True):
        #    GameButtonPress()

# start a thread tha will keep watch at arduino Serial
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
    return "units";

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# start a new game, 
# define order and sent appropriate messages.
# all AMBER  
def StartNewGame():
    pass;

# register the unit_id in the host
def GameRegister():
    pass;

# unregister the unit_id in the host
def GameUnregister():
    pass;

# get a list of tasks for this unit
def GameGetTasks():
    pass;

def GameButtonPress():
    pass;

# handle & execute all available tasks
# return a list of required actions
def GameHandleTasks(tasks):
    pass;

# __ONLY__ WHEN GAME CONTROL IS ACTIVE 
# for each action, send appropriate message to host
def GamePostActions(actions):
    pass;


# ENTRY POINT
def main():
    parse_argv();    
    initGateway();
    
    try:
        GameRegister();
        if GAME_CONTROL:
            units = GameListUnits() 
            StartNewGame(units)
    except Exception as err:
        print(err)
        exit(-1);
    
    while(True):
        try:
            tasks = GameGetTasks()
            actions = GameHandleTasks(tasks)
            if GAME_CONTROL:
                GamePostActions(actions)
        
        except Exception as err:
            # what should be done when error happens ? ?
            print(err);

        time.sleep(LOOP_DELAY);
                    

if __name__ == '__main__':    
    main();
