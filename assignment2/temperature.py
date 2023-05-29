#!/usr/bin/python

## This program is designed to run on the gateway/Raspberry Pi.
## The program is used as an interface (gateway) between the Raspberry Pi
## and the end user in the 2nd assignment of the laboratory work.
## The program is then extended in the 3rd assignment to communicate with 
## a server that will store the measurements from the Arduino.
##
## Tip: There is one method called debug built in the code to make it easier
##      to print out variables or debug messages.
##      Example  debug("Test!") - Prints the text Test! on line 20.
##      Example2 debug("{}".format(tempThresh) - Prints the temperature 
##                                               threshhold on line 20.
##

from colorama import Fore, Back, Cursor, Style, init
import select
import random
import sys
import time
import os
import serial
import socket
import json

from datetime import datetime

##############################################
##                                          ##
##                Variables                 ##
##                                          ##
##############################################
# Network variables.
id = 0 # Todo: Set your three digits from your LiU-ID here.
host = '130.236.81.13'
#host = '0.0.0.0'
port = 8718
sock = None;

ser = serial.Serial('/dev/ttyACM0',9600)

# Temperature variables.
temperature = 0.0
tempThresh = 18

# Humidity variables.
humidity = 0.0
humidThresh = 50

# Input command variable.
command = None

# Update variables
updateFrequency=1 # seconds.
lastUpdated = None

##############################################
##                                          ##
##              Main function               ##
##                                          ##
##############################################

# This is the main method that loops forever.
def main():
    init()
    printMenu()
    ser.read(ser.inWaiting())
    while True:
            try:
                readMeasurements()
                sendInstructions()
                getInput()
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                print(e)


##############################################
##                                          ##
##        Functions for assignment 2        ##
##                                          ##
##############################################

# This method reads the measurements and stores the data in global variables.
#
# This is a part of the 2nd assignment of the laboratory work.
# Consult the following sites to solve this task:
# Serial: https://pyserial.readthedocs.io/en/latest/shortintro.html
def readMeasurements():
    global lastUpdated
    global temperature
    global humidity
    
    # Checking if we need to update the measurements.
    if (lastUpdated is None or 
    (lastUpdated is not None and int(time.time()-lastUpdated)>updateFrequency)):
        
        # Looping through all incommed measurements.
        # 12 bytes = [sign]XX.XX[sign]YY.YY where XX.XX is temperature and 
        # YY.YY is the humidity.
        while ser.inWaiting() > 12:
            # Reading a measurement
            # Todo: read 12 bytes of data and store in a local variable. Use the
            #       ser variable.
            data_str = ser.read(12).decode("utf-8");
            temperature = float(data_str[0:6]);
            humidity = float(data_str[7:]);

            #print(temperature)                        
            #print(humidity)                        
            # Sets the values.
            # Todo: Extract the temperature and humidity from the data 
            #       variable and store them in the global variables for
            #       temperature and humidity. Tip cast the extracted values 
            #       to float.
        
        # Sending measurements to the server.
        sendMeasurements()
        
        # Updating the terminal.
        updateTerminalMetrics()
        
        # Updating the time variable.
        lastUpdated = time.time()


# This method sends instructions to the Arduino over the serial connection.
# The instructions are two bytes with either 0 or 1 to turn off or on the LEDs
#
# This is a part of the 2nd assignment of the laboratory work.
# Consult the following sites to solve this task:
# Bytearrays: https://docs.python.org/3.1/library/functions.html#bytearray
# Serial: https://pyserial.readthedocs.io/en/latest/shortintro.html 
def sendInstructions():
    # Creating LED instructions
    # 1 = High, 0 = Low.
    
    # Todo: Create a bytearray with the size of 2. If the temperature or 
    #       humidity is above the set threshhold the first byte should be set
    #       to 0 and the second byte to 1. If both values are below the set
    #       threshhold then the first byte should be set to 1 and the second to
    #       0.
    instructions = bytearray([0,0])
    if(temperature > tempThresh): 
        instructions[0] += 1;

    
    if(humidity > humidThresh):
        instructions[0] += 2;
     
    
    # Sending LED instructions.
    # Todo: Sen the bytearray with LED instructions to the Arduino, use the ser
    #       variable.
    ser.write(instructions);
    #print(instructions)
##############################################
##                                          ##
##        Functions for assignment 3        ##
##                                          ##
##############################################

# This method packets the measurements to a message and sends it to the server.
# The response from the server contains the latest threshhold of the 
# temperature and humidity.
#
# This is a part of the 3rd assignment of the laboratory work.
# Consult the following sites to solve this task:
# Dictionaries: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
def sendMeasurements():
    global tempThresh
    global humidThresh
    
    # Todo: Create a dictionary with the following keys: 
    #       message_type, id, temperature, humidity.
    #       The message_type shall be "TNK116UpdateMeasurements".
    request = {
        "message_type":"TNK116UpdateMeasurements",
        "id":id,
        "humidity": humidity,
        "temperature": temperature,
        "time": str(datetime.now())
    }
    
    # Passes the request to a method that handes server connections.
    # A successfull response will have the following fields: message_type, 
    # temperature_threshold, humidity_threshold
    # A failed respons will have a message_type that is equal to "ERROR".
    response = sendToServer(request)
    
    # Todo: Make a check that the response is not an error response and update
    #       the temperature and humidity thresholds.
    if not (response["message_type"] == "TNK116UpdateMeasurements_Response"):
        print("Error on response, sad!");
        exit(-1);


# This method packets a update command to a message and sends it to the server.
# The response from the server contains a sucess or fail.
#
# This is a part of the 3rd assignment of the laboratory work.
# Consult the following sites to solve this task:
# Dictionaries: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
def updateThreshold(type,value):

    # Todo: Create a dictionary with the following keys: 
    #       message_type, id, type, value.
    #       The message_type shall be "TNK116SetThreshold".
    request = {
        "message_type":"TNK116SetThreshold",
        "id":id,
        "type": type,
        "value": value,
        "time": str(datetime.now())
    }
    
    # Passes the request to a method that handes server connections.
    # The response will be a dictionary with the following fields: 
    # message_type, sucess
    # If something gets wrong with the request then the response 
    # message_type will be equal to "ERROR".
    response = sendToServer(request)
    
    # Todo: Return the value of the field sucess. 
    #       Return False if the request failed.
    return True

# This method handles connections to the server and parses the response 
# as a JSON dictionary.
#
# This is a part of the 3rd assignment of the laboratory work.   
# Consult the following sites to solve this task:
# Socket (client): https://docs.python.org/3/library/socket.html#example
# JSON encode(dumps) and decode(loads): https://docs.python.org/3/library/json.html
def sendToServer(request):
    # Creating a socket and connects to the set host and port.
    # Todo: Make a socket and connect to the host.

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((host, port))
    
    # Dumps the request dictionary as a JSON object.
    # Sending the JSON message to the host. Note: The message must end with a | 
    # character and the String should be encoded to bytes with .encode().
    # Todo: Create a JSON message and send it to the host with a trailing |.
    req_json = json.dumps(request);
    req_json = req_json + "|";
    sock.send(req_json.encode("utf-8"));

    # Reading input from the host.
    # Todo: Read the input from the host.
    data = sock.recv(2048);
    received = data.decode();
    
    # Closing the connection to the server.
    # Todo: Use the close() method on the socket.
    sock.close();

    received = received[:-1];

    # Creates a string from the receive bytes, removes the trailing | and parses
    # the string as a JSON dictionary.
    # Note the | must be removed from the string before the string is 
    # loaded as a JSON dictionary.
    # Todo: Transform the recived bytes to a JSON dictionary.
    response = json.loads(received)

    return response;
 
##############################################
##                                          ##
##              Input functions             ##
##                                          ##
##############################################

# This method reads the command from from the standard input (keyboard)
def getInput():
    global command
    global tempThresh
    global humidThresh

    # Printing menu choise question.
    if command is None:
        printMenuSelector(0)
        command = ""
    # Handling menu choises.
    if '\n' in command:
        choise = command.strip()
        
        # Handling temperature threshhold.
        if choise == '1':
            printMenuSelector("Set temperature threshhold ({}): "
                              .format(tempThresh))
            value = input()
            value = float(value.replace(',','.'))
            if updateThreshold('temperature',value):
                tempThresh = value
            
        # Handling humidity threshhold.
        elif choise == '2':
            printMenuSelector("Set humidity threshhold ({}): "
                              .format(humidThresh))
            value = input()
            value = float(value.replace(',','.'))
            if updateThreshold('humidity',value):
                humidThresh = value
            
        # Handling exit command.
        elif choise == '3':
            printMenuSelector("Exiting...\n")
            sys.exit()
        
        command = None
        return
    
    # Waiting 1 secod for new commands.
    readReady, writeReady, exceptReady = select.select([sys.stdin], [], [],1)
    
    # Appending new commands to the command variable
    if len(readReady):
        line = sys.stdin.readline()
        command = command+line
        return


##############################################
##                                          ##
##            Graphical functions           ##
##                                          ##
##############################################

def printMenu():
    # Clearing the screen.
    os.system('clear')
    
    # Printing the header
    sys.stdout.write('{message:#<33}\n'.format(message=""))
    sys.stdout.write('#{}#\n'.format("Temperature gateway".center(31," ")))
    sys.stdout.write('{message:#<33}\n'.format(message=""))
    sys.stdout.write("# Temp: 00.00\t   Humid: 00.00 #\n")
    sys.stdout.write("{message:#<33}\n".format(message=""))
    
    # Creating the menu.
    menu = {}
    menu['1'] = "Set temperature threshold."
    menu['2'] = "Set Humidity threshold."
    menu['3'] = "Exit."
    
    # Printing the menu
    menuItems=menu.keys()
    for menuItem in menuItems:
        sys.stdout.write("#{message: <31}#\n".format(message="{}. {}"
                         .format(menuItem,menu[menuItem])))
    sys.stdout.write("#{message: <31}#\n".format(message=""))
    sys.stdout.write("{message:#<33}\n".format(message=""))
    sys.stdout.flush()
    
def updateTerminalMetrics():
        # Storing cursor position.
        sys.stdout.write("\033[s")
        
        # Moving to temperature position.
        # Changing color depending on threshhold.
        sys.stdout.write("\033[4;9H")
        if temperature > tempThresh:
            sys.stdout.write(Fore.RED)
        sys.stdout.write("{:.2f}".format(temperature))
        sys.stdout.write(Style.RESET_ALL)
        
        # Moving to humidity position.
        # Changing color depending on threshhold.
        sys.stdout.write("\033[4;27H")
        if humidity > humidThresh:
            sys.stdout.write(Fore.RED)
        sys.stdout.write("{:.2f}".format(humidity))
        sys.stdout.write(Style.RESET_ALL)
        
        # Restoring the cursor position.
        sys.stdout.write("\033[u")
        sys.stdout.flush()

def printMenuSelector(question):
    # Moving to the right spot.
    sys.stdout.write("\033[11;0H")
    
    # Clearing row.
    sys.stdout.write("\033[K")
    if question == 0:
        question = "Please select: "
    
    # Printing question.
    sys.stdout.write(question)
    
    # Moving cursor.
    sys.stdout.flush()

def debug(text):
    # Storing cursor position.
    sys.stdout.write("\033[s")
    
    # Moving cursor.
    sys.stdout.write("\033[20;0H")
    
    # Clearing row.
    sys.stdout.write("\033[K")
    
    # Writing debug
    sys.stdout.write("DEBUG: {}".format(text))

    # Restoring the cursor position.
    sys.stdout.write("\033[u")
    sys.stdout.flush()

if __name__=="__main__":
    main()
