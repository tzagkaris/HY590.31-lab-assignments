const int LED_RED = 9;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.print("Hello");
  pinMode(LED_RED, OUTPUT);
  digitalWrite(LED_RED, HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:

}
