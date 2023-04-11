import serial, sys

with serial.Serial(port=sys.argv[1], baudrate=sys.argv[2]) as ser:
    while ser.isOpen():
        print(ser.readline());
