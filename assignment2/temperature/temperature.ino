/*
 * TNK116 - Internet of Things
 * Sketch for blink
 * Board Arduino UNO
 * 1 x green LED
 * 1 x red LED
 * 1 x DHT22 (Temperature/Humidity sensor)
 */

// Including 3rd party software for reading DHT22.
#include "DHT.h"
#include "Adafruit_Sensor.h"

// Declaring pin and sensor type.
// Todo: Change the "PIN_NR" to pin number for the input pin of the 
//       temperature sensor

#define DHTPIN 11
#define DHTTYPE DHT22

// Declaring a DHT object. 
DHT dht(DHTPIN, DHTTYPE);

// Declaring variable to store LED instructions.
byte instructions[2] = {1,0};

// Selecting the pins for the LED (green)
// Todo: Set the right pin number for the green and red LED.
const int LED_GREEN = 12;
const int LED_RED = 13;
//const int LED_BLUE = 8;

float temperature, humidity;

// This method sends measurements to the Raspberry pi over the serial 
// connection. The Raspberry pi assumes that the sign + or - is sent and that
// the mesurement has two digits and two decimals.
//
// Consult the following sites to solve this task:
// Serial: https://www.arduino.cc/reference/en/language/functions/communication/serial/print
void printMeasurement(float value)
{
  // Printing sign.
  // Todo: Check if the value is positive or negative and print the sign + or -
  //       to the serial bus
  if(value < 0.0) {
    Serial.print("-");
  }
  else {
    Serial.print("+");
  }
  

  // Padding values that only have 1 digit with an extra 0.
  // Todo: Check it the values only has 1 digit and if so send an 0 to the 
  //       serial bus.
  if(value < 10.0) {
    Serial.print("0");
  }
  
  // Printing value.
  // Todo: Send the absolute value to the serial bus.
  Serial.print(value);
}

// This method reads instructions from the serial bus and sets the LED-diods
// to low or high depending on the instructions. The instructions are two bytes.
//
// Serial: https://www.arduino.cc/reference/en/language/functions/communication/serial/print
void updateLEDs()
{
  // Reading the instructions from the serial bus.
  while(Serial.available()>=2)
  {
	  // Todo: Read two bytes from the serial bus into the instructions 
	  //       variable.
    Serial.readBytes(instructions, 2);
  }
  
  //if(instructions[0] == 1) {
  //  digitalWrite(LED_BLUE, HIGH);
  //}

  // Sets the green LED to high if the first bit in the instructions variable
  // is a 1 and sets the green LED to low if the first bit of the instructions
  // variable is 0.
  
  // Todo: Set the green LED to low/high depending on the first bit of the 
  //       instructions variable.
  
  if((instructions[0] & 1)  == 1) {
    digitalWrite(LED_GREEN, HIGH);
  } else {
    digitalWrite(LED_GREEN, LOW);
  }
  
  //Serial.println(bitRead(instructions[0], 0));
  
  
  // Sets the red LED to high if the second bit in the instructions variable
  // is a 1 and sets the red LED to low if the second bit of the instructions
  // variable is 0.
  
  // Todo: Set the red LED to low/high depending on the second bit of the 
  //       instructions variable.
  
  if(((instructions[0] & 2)>>1)  == 1) {
    digitalWrite(LED_RED, HIGH);
  } else {
    digitalWrite(LED_RED, LOW);
  }
}

void setup() {
  // Setup for that runs once in the beginning.
  // Defining the type of pins, in this case output.
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  // Initializing the DHT sensor.
  dht.begin();
  
  // Setting the green pin to high.
  //digitalWrite(LED_GREEN, HIGH);
  
  
  // Starting a serial connection.
  Serial.begin(9600);
}

// This is the main loop of the Arduino code. 
void loop() 
{
  // Reading the temperature and humidity from the sensor.
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  
  // Restarts the loop after 1 second if no measurements was read.
  if (isnan(temperature) || isnan(humidity)) { 
	// Waiting 1 second.
	delay(1000);
	return;
  }
  
  // Printing statistics to the serial connection.
  //Serial.println(temperature);
  //Serial.println(humidity);
  printMeasurement(temperature);
  printMeasurement(humidity);

  updateLEDs();

  // Waiting 1 second.
  delay(1000);
}
