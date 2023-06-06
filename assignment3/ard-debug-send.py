import serial
import threading
import time
import sys

serial.Serial.timeout = None;

ser = serial.Serial('/dev/ttyACM0',9600)

#def buttonCheckLoop():
#    print("works")
#    while(True):
#        read = ser.read(); # blocking call
#        print("Got: " + str(read))

#threading.Thread(target=hello, args=(1, ), daemo)
#time.sleep(100)

ser.write(bytes(chr(int(sys.argv[1])).encode("ascii")))
time.sleep(0.25);
ser.close();
#while(True):
#    read = ser.read(); # blocking call
#    print("Got: " + str(read))