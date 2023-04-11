/*
 * TNK116 - Internet of Things
 * Sketch for Smartbin:
 * Weight and distance sensing and LED actuation.
 * Board Arduino UNO
 * 1 x ultrasonic distance sensor, HC-SR04 
 * 1 x weight sensor, Square Force-Sensitive Resistor
 * 1 x green LED
 * 1 x yellow LED
 * 1 x red LED
 * 1 x potentiometer or sutable resistor as a pull-down resistor for the weight sensor
 */

// Setting the pins for the sensors and the LEDs.
// TODO: Set the pins according to your build.
const int WEIGHT_SENSOR_PIN = 0;
const int LED_GREEN = 11;

// Setting variables.
int weightValue;

// Setup for that runs once in the beginning.
// Defining the type of pins and starting a serial connection.
void setup() {
  // declare the ledPin as an OUTPUT:
  Serial.begin(9600);
  pinMode(LED_GREEN, OUTPUT);  
  digitalWrite(LED_GREEN, HIGH);
}

// This code will be run forever as a loop.
void loop() {
  // read the value from the weight sensor:
  weightValue = analogRead(WEIGHT_SENSOR_PIN);
  // Printing the weight and distance to the serial port  
  Serial.println(weightValue);

  // Delaying the code for 100 ms before the loop restarts.
  delay(1000);
}
