/*
 * TNK116 - Internet of Things
 * Sketch for Distance sensing and LED actuation
 * Board Arduino UNO
 * 1 x ultrasonic distance sensor HC-SR04 
 * 1 x green LED
 * 1 x red LED
 */

// Setting the pins for the sensor and the LEDs.
// TODO: Set the pins according to your build.
const int trigPin = 13;
const int echoPin = 12;
const int LED_RED = 9;
const int LED_GREEN = 11;
const int LED_YELLOW = 10;

// Setting variables.
float duration, distance;

// Setup for that runs once in the beginning.
// Defining the type of pins and starting a serial connection.
void setup() {
  // TODO: Define the type of pin for the 4 pins.
  Serial.begin(9600);

  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);

  pinMode(trigPin, OUTPUT); 
  pinMode(echoPin, INPUT);

  //digitalWrite(LED_YELLOW, HIGH);
}

// This code will be run forever as a loop.
void loop() {
  //Setting initial paramaters for the HC-SR04 pins
  digitalWrite(trigPin, LOW);
  
  // Delaying the code and then sends a trigger pulse.
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Reading the measurements from the HC-SR04.
  duration = pulseIn(echoPin, HIGH);
  // Serial.println(duration);
  // Calculating the distance in cm.
  // TODO: Read the specifications of the HC-SR04 to learn how calculate the 
  // distance from the duration. The specifications are found on Lisam.
  distance = duration * 0.034 / 2;
  
  // Lights up the red LED if the distance is shorter than 10 cm.
  if (distance <=10){
    digitalWrite(LED_GREEN,LOW);
    digitalWrite(LED_RED, HIGH);
  }
  // Lights up the green LED if the distance is longer than 10 cm.
  else {
    digitalWrite(LED_GREEN,HIGH);
    digitalWrite(LED_RED, LOW);
  }
  
  // Printing the distance on the serial port
  Serial.println(distance);
  
  // Delaying the code for 100 ms before the loop restarts.
  delay(300);
}