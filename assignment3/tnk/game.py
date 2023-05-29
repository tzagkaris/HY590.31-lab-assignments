#!/usr/bin/python

## This program is designed to run on the Raspberry Pi or another PC.
## The program is used as an interface end user in the laboratory work
## assignment.
##
## Tip: There is one method called output built in the code to make it easier
##      to print out variables or debug messages.
##      Example  output("Test!") - Prints the text Test! to the output window
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

##############################################
##                                          ##
##                Variables                 ##
##                                          ##
##############################################
# Network variables.
user_id = None
host = '130.236.81.13'
port = 8718

#Input command variable
command = None

# Output print row.
outputRow = 0

# Update variables
updateFrequency=1 # seconds.

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
                # Checking for new service responses.
                checkServiceResponses()
                # Handles input and waits.
                getInput()
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                time.sleep(1)
                output(e)
    # Clearing the screen.
    os.system('clear')

# This method query the server for new service responses.
def checkServiceResponses():
    if user_id is None:
        return
    
    # Creating a request for new service responses.
    request = {"message_type":"TNK116Lab3GetTasks","user_id":user_id}
    
    # Passes the request to a method that handes server connections.
    response = sendToServer(request)

    # Stops the method if no new service response was found.
    if response["tasks"] is None or len(response["tasks"]) == 0:
        return
    
    # Printing all service responses to the output area.
    tasks = response["tasks"]
    for task in tasks:
        outputString = "Response from service {}:".format(
                        task["service_id"])
        for parameter in task["data"]:
            outputString = "{} {}={}".format(outputString,parameter,
                                             task["data"][parameter])

        output(outputString)

# This method query the server for a list of available services for the user.
def listServices():

    if user_id is None:
        return
    
    # Creating a request for a list of available services.
    request = {"message_type":"TNK116Lab3ListServices","user_id":user_id}
    
    # Passes the request to a method that handes server connections.
    response = sendToServer(request)
    
    # Stops the method if no available services was found.
    if response["available_services"] is None:
        return

    # Printing all available services to the output area.    
    output("{} | {} | {} | {}".format("service id", "unit id", "name","input"))
    for service in response["available_services"]:
        output("{} | {} | {} | {}".format(service["service_id"],
            service["unit_id"], service["service_name"], service["input"]))

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


# This method sends a request to run a service to the server.
def requestService():

    # Asking for the service id on the service that shall run.
    printMenuSelector("Set service id: ")
    service_id = input()
    try:
        service_id = int(service_id)
    except Exception as e:
        output(e)
        return

    # Creating a request for a list of the parameters that is needed for the service.
    request = {"message_type":"TNK116Lab3ListServices","user_id":user_id,
               "service_id":service_id}
    
     # Passes the request to a method that handes server connections.   
    response = sendToServer(request)

    # Stops the method if the service was not found.
    if (response["available_services"] is None or
       len(response["available_services"]) == 0):
        output("No service with that id")
        return

    # Extracts the parameters.
    service = response["available_services"][0]
    parameters = json.loads(service["input"])

    # Looping through all parameters and asks to set them.
    for parameter in parameters:
        printMenuSelector("Set {}({}): ".format(parameter,
                                                parameters[parameter]))
        value = input()
        # parses the parameter as a float, int, boolean or text.
        try:
            if parameters[parameter] == "float":
                parameters[parameter] = float(value)
            elif parameters[parameter] == "int":
                parameters[parameter] = int(value)
            elif parameters[parameter] == "boolean":
                parameters[parameter] = bool(value)
            else:
                parameters[parameter] = value
        except Exception as e:
            output(e)
            return

    # Creating a request for running the service.
    request = {"message_type":"TNK116Lab3RequestService","user_id":user_id,
               "service_id":service_id, "data":parameters}

    # Passes the request to a method that handes server connections. 
    response = sendToServer(request)

    # Prints to the output area if it was successful.
    if response["success"]:
        output("Service requested. ")
    else:
        output("Service request failed. ")

# This method sets the user id.
def updateUserId():
    global user_id

    # Asking for the user id for the session.
    printMenuSelector("Set user id: ")
    user_id = input()

    # Sets the user id.
    try:
        user_id = int(user_id)
    except Exception as e:
        user_id = None
        output(e)
        return
    
    # Storing cursor position.
    sys.stdout.write("\033[s")
        
    # Updating user id
    sys.stdout.write("\033[4;1H")
    sys.stdout.write('#{message: <31}#\n'.format(
        message="User id: {}".format(user_id)))
     
    # Restoring the cursor position.
    sys.stdout.write("\033[u")
    sys.stdout.flush()
    
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
            updateUserId()
            
        # Handling listing of services.
        elif choise == '2':
            listServices()
            
        # Handling running of services
        elif choise == '3':
            requestService()            
            
        # Handling exit command.
        elif choise == '4':
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
    sys.stdout.write('#{}#\n'.format("Service control".center(31," ")))
    sys.stdout.write('{message:#<33}\n'.format(message=""))
    sys.stdout.write('#{message: <31}#\n'.format(message="User id: "))
    sys.stdout.write('{message:#<33}\n'.format(message=""))
    
    # Creating the menu.
    menu = {}
    menu['1'] = "Set user id."
    menu['2'] = "List services."
    menu['3'] = "Run service."
    menu['4'] = "Exit."
    
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
        sys.stdout.write("\033[15;1H")

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
    sys.stdout.write("\033[11;0H")
    
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
        sys.stdout.write("\033[{};1H".format(18+outputRow))
    
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
