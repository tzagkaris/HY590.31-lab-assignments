import serial, sys

f = open(sys.argv[3], 'w');
# sample count
samples = 5000;
with serial.Serial(port=sys.argv[1], baudrate=sys.argv[2]) as ser:
    while ser.isOpen():
        print("On sample: " + str(samples))
        samples = samples - 1;
        if samples == 0: 
                break;
        line = str(ser.readline())
        reading = line.split("\'", 1)[1].split("\\r")[0]
        f.write(reading + '\n')

