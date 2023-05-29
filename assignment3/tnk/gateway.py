#!/usr/bin/python

## This program is designed to run on the Raspberry Pi.
## The program is used as an gateway for the Arduino in the laboratory work
## assignment.
##
## Tip: There is one method called output built in the code to make it easier
##      to print out variables or messages.
##      Example  output("Test!") - Prints the text Test! in the output area.
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
import textwrap
from datetime import datetime

##############################################
##                                          ##
##                Variables                 ##
##                                          ##
##############################################
# Network variables.
unit_id =  None # Todo: Set the unit id here.
host = '130.236.81.13'
port = 8718

# Serial connection variables.
ser = serial.Serial('/dev/ttyACM0',9600)

#Input command variable
command = None

# Output print row.
outputRow = 0

# Update variables
updateFrequency=1 # seconds.

# Task list
taskList = []

# Arduino reading variables
messageType = None
length = None

# Game master
gameMaster = None

##############################################
##                                          ##
##              Main function               ##
##                                          ##
##############################################

# This is the main method that loops forever.
def main():
    init()
    # Printing menu.
    printMenu()
    # Printing output section.
    printOutputSection()
    while True:
            try:
                # Checking for new service requests.
                loadServiceRequests()
		# Reading response from the Arduino.
                readFromArduino()
				
		# Handle service requests.
                handleServiceRequests()
				
		# Handles input and waits.
                getInput()
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                time.sleep(1)
                output(e)
    # Clearing the screen.
    os.system('clear')



# This method query the server for new service requets.
def loadServiceRequests():
    global taskList
    
    if unit_id is None:
        output("Unit id is not set.")
        return

    # Creating a request for new services.
    request = {"message_type":"GameGetTasks","unit_id":unit_id}
    
    # Passes the request to a method that handes server connections.
    response = sendToServer(request)

    # Stops the method if no new service request was found.
    if response["tasks"] is None or len(response["tasks"]) == 0:
        return

    # Adding all new service requests to the task list.
    tasks = response["tasks"]
    for task in tasks:
        outputString = "Service request received {} from unit {}".format(
                        task["data"]["action"],task["from"])

        output(outputString)

        task["completed"] = False
    
        taskList.append(task)

##############################################
##                                          ##
##        Functions for assignment 3        ##
##                                          ##
##############################################

# This method handles the tasks in the task list.
# The tasks can either be one time actions or tasks that
# persist over a longer period of time.
def handleServiceRequests():
    global taskList
    global gameMaster
    
    # Looping though all taks in the list.
    for task in taskList:
        if task["data"]["action"] == "BUTTON_CHANGE":
            output("Button change") # TODO: Implement button change behaviour.
            task["completed"] = True
            
        elif task["data"]["action"] == "CHANGE_LED":
            output("Change led") # TODO: Implement led change behaviour.
            #sendInstructions(None,0) #Todo: Change the None to the match the arduino code.
            task["completed"] = True
            
        elif task["data"]["action"] == "GAME_REGISTRATION":
            output("Game registration") # TODO: Implement game registration behaviour.
            task["completed"] = True
            
        elif task["data"]["action"] == "PLAY_GAME":
            if task["data"]["game_state"] == "START":
                gameMaster = task["from"]
            elif task["data"]["game_state"] == "STOP":
                gameMaster = None
            
            task["completed"] = True
        
        elif task["data"]["action"] == "PLAY_SOUND":
            task["completed"] = True # Not used.
            
            
        # Checks if the task is completed.
        if task["completed"]:

            # Sends the response to the user.
            outputString = "Service {} is completed for user {}".format(
                        task["data"]["action"],task["from"])
            output(outputString)

            # Removes the task
            taskList.remove(task)
        
# This method handles connections to the server and parses the response 
# as a JSON dictionary.
def sendToServer(request):
    # Creating a socket and connects to the set host and port.
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    clientsocket.connect((host, port))    
    
    # Dumps the request dictionary as a JSON object.
    # Sending the JSON message to the host. Note: The message must end with a | 
    # character and the String should be encoded to bytes with .encode().
    clientsocket.send("{}|".format(json.dumps(request)).encode())    
    
    # Reading input from the host.
    receive = clientsocket.recv(1024)
    
    # Closing the connection to the server.
    clientsocket.close()                   

    # Creates a string from the receive bytes, removes the trailing | and parses
    # the string as a JSON dictionary.
    # Note the | must be removed from the string before the string is 
    # loaded as a JSON dictionary.
    response = json.loads(str(receive,'utf-8').replace("|",""))

    return response

# This method reads data from the Arduino.
def readFromArduino():
    global messageType
    global length

    # Checks if no message is in the pipe.
    if messageType is None:
        # Checks if all bytes for the type and length has arrived.
        if ser.inWaiting() >= 3:
            # Reads the messageType (first byte) and the message length (next two bytes) and stores them as integers.
            messageType = int(str(ser.read(1),'utf-8'))
            length = int(str(ser.read(2),'utf-8'))            
#            output("Receiving {}{}".format(messageType,length)) # Can be used for debugging.

    # Checks if a message is in the pipe.
    if messageType is not None:
        # Checks if all bytes for the message has arrived.
        if ser.inWaiting() >= length:
            # Reads the message.
            message = ser.read(length)
#            output("Receiving {}".format(str(message,'utf-8'))) # Can be used for debugging.
            # Sends the message to the response handler as a string with extra null bytes removed.
            handleArduinoResponse(messageType, length, str(message,'utf-8').rstrip('\x00'))

            # Setting the message as handled by setting the message type and length to None.
            messageType = None
            length = None


# This method handles responses from the Arduino and do stuff with it.
def handleArduinoResponse(messageType, length, message):
    global taskList
    # Handles messages from the arduino.
    if messageType == None: # Todo: Change the None a more suitable id such as 1.
        # Todo: Handle button action by creating a task.
        
        
    
# This method sends measurements to the Arduino over the serial 
# connection. The data is sent in a TLV structure. [Type][Length][Value].
# The size of the type field is 1 byte.
# The size of the length field is 2 bytes.
# The size of the value field varies.
def sendInstructions(messageType, value):
    value = str(value)
#    output("Sending: {}{:02}{}".format(messageType,len(value),value)) # Useful for debugging.
    # Sends the TLV message to the Arduino as a string.
    ser.write("{}{:02}{}".format(messageType,len(value),value).encode())


##############################################
##                                          ##
##              Input functions             ##
##                                          ##
##############################################

# This method reads the command from from the standard input (keyboard)
def getInput():
    global command

    # Printing menu choise question.
    if command is None:
        printMenuSelector(0)
        command = ""
    # Handling menu choises.
    if '\n' in command:
        choise = command.strip()
        
        # Handling setting of user id.
        if choise == '1':
            # Clearing the screen.
            os.system('clear')
            
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
    sys.stdout.write('#{}#\n'.format("Gateway".center(31," ")))
    sys.stdout.write('{message:#<33}\n'.format(message=""))
    sys.stdout.write('#{message: <31}#\n'.format(message="Unit id: {}".format(unit_id)))
    sys.stdout.write('{message:#<33}\n'.format(message=""))
    
    # Creating the menu.
    menu = {}
    menu['1'] = "Exit."
    
    # Printing the menu
    menuItems=menu.keys()
    for menuItem in menuItems:
        sys.stdout.write("#{message: <31}#\n".format(message="{}. {}"
                         .format(menuItem,menu[menuItem])))
    #sys.stdout.write("#{message: <31}#\n".format(message=""))
    sys.stdout.write("{message:#<33}\n".format(message=""))
    sys.stdout.flush()
    
def printOutputSection():
        # Storing cursor position.
        sys.stdout.write("\033[s")
        
        # Moving to temperature position.
        # Changing color depending on threshhold.
        sys.stdout.write("\033[12;1H")

        sys.stdout.write('{message:#<80}\n'.format(message=""))
        sys.stdout.write('#{}#\n'.format("Output".center(78," ")))
        sys.stdout.write('{message:#<80}\n'.format(message=""))
        for i in range(1,16):
            sys.stdout.write('#{}#\n'.format("".center(78," ")))
        sys.stdout.write('{message:#<80}\n'.format(message=""))
        # Restoring the cursor position.
        sys.stdout.write("\033[u")
        sys.stdout.flush()

def printMenuSelector(question):
    # Moving to the right spot.
    sys.stdout.write("\033[8;0H")
    
    # Clearing row.
    sys.stdout.write("\033[K")
    if question == 0:
        question = "Please select: "
    
    # Printing question.
    sys.stdout.write(question)
    
    # Moving cursor.
    sys.stdout.flush()

def output(text):
    global outputRow

    lines = lines = textwrap.wrap(str(text).strip(), 78, break_long_words=False)
    
    # Storing cursor position.
    sys.stdout.write("\033[s")
    
    # Writing debug
    for line in lines:
        # Moving cursor.
        sys.stdout.write("\033[{};1H".format(15+outputRow))
    
        # Clearing row.
        sys.stdout.write("\033[K")
    
        sys.stdout.write("#{message: <78}#\n".format(message="{}"
                             .format(line.strip())))
        outputRow = (outputRow + 1) % 15
    
    # Restoring the cursor position.
    sys.stdout.write("\033[u")
    sys.stdout.flush()

if __name__=="__main__":
    main()
