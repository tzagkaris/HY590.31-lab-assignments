
#define NOTE_B0  31
#define NOTE_C1  33
#define NOTE_CS1 35
#define NOTE_D1  37
#define NOTE_DS1 39
#define NOTE_E1  41
#define NOTE_F1  44
#define NOTE_FS1 46
#define NOTE_G1  49
#define NOTE_GS1 52
#define NOTE_A1  55
#define NOTE_AS1 58
#define NOTE_B1  62
#define NOTE_C2  65
#define NOTE_CS2 69
#define NOTE_D2  73
#define NOTE_DS2 78
#define NOTE_E2  82
#define NOTE_F2  87
#define NOTE_FS2 93
#define NOTE_G2  98
#define NOTE_GS2 104
#define NOTE_A2  110
#define NOTE_AS2 117
#define NOTE_B2  123
#define NOTE_C3  131
#define NOTE_CS3 139
#define NOTE_D3  147
#define NOTE_DS3 156
#define NOTE_E3  165
#define NOTE_F3  175
#define NOTE_FS3 185
#define NOTE_G3  196
#define NOTE_GS3 208
#define NOTE_A3  220
#define NOTE_AS3 233
#define NOTE_B3  247
#define NOTE_C4  262
#define NOTE_CS4 277
#define NOTE_D4  294
#define NOTE_DS4 311
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_FS4 370
#define NOTE_G4  392
#define NOTE_GS4 415
#define NOTE_A4  440
#define NOTE_AS4 466
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_CS5 554
#define NOTE_D5  587
#define NOTE_DS5 622
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_FS5 740
#define NOTE_G5  784
#define NOTE_GS5 831
#define NOTE_A5  880
#define NOTE_AS5 932
#define NOTE_B5  988
#define NOTE_C6  1047
#define NOTE_CS6 1109
#define NOTE_D6  1175
#define NOTE_DS6 1245
#define NOTE_E6  1319
#define NOTE_F6  1397
#define NOTE_FS6 1480
#define NOTE_G6  1568
#define NOTE_GS6 1661
#define NOTE_A6  1760
#define NOTE_AS6 1865
#define NOTE_B6  1976
#define NOTE_C7  2093
#define NOTE_CS7 2217
#define NOTE_D7  2349
#define NOTE_DS7 2489
#define NOTE_E7  2637
#define NOTE_F7  2794
#define NOTE_FS7 2960
#define NOTE_G7  3136
#define NOTE_GS7 3322
#define NOTE_A7  3520
#define NOTE_AS7 3729
#define NOTE_B7  3951
#define NOTE_C8  4186
#define NOTE_CS8 4435
#define NOTE_D8  4699
#define NOTE_DS8 4978
#define REST      0


// change this to make the song slower or faster
int tempo = 144;

// change this to whichever pin you want to use
int buzzer = 6;

// notes of the moledy followed by the duration.
// a 4 means a quarter note, 8 an eighteenth , 16 sixteenth, so on
// !!negative numbers are used to represent dotted notes,
// so -4 means a dotted quarter note, that is, a quarter plus an eighteenth!!
int melody_win[] = {

  //Based on the arrangement at https://www.flutetunes.com/tunes.php?id=192
  
  NOTE_G6, 12,  NOTE_FS6,12,  NOTE_DS6,12,  NOTE_A6,12,  NOTE_GS5,12,  NOTE_E6,12,
  NOTE_GS6, 12,  NOTE_C7,12,

};

int melody_lose[] = {

  //Based on the arrangement at https://www.flutetunes.com/tunes.php?id=192
  
  NOTE_A5, -8,  NOTE_GS4,-8,  NOTE_G4,-8,  NOTE_FS4,-8,  NOTE_F4,1,  NOTE_E4,2,
  

};


// sizeof gives the number of bytes, each int value is composed of two bytes (16 bits)
// there are two values per note (pitch and duration), so for each note there are four bytes
int notes_win = sizeof(melody_win) / sizeof(melody_win[0]) / 2;
int notes_lose = sizeof(melody_lose) / sizeof(melody_lose[0]) / 2;

// this calculates the duration of a whole note in ms
int wholenote = (60000 * 4) / tempo;

int divider = 0, noteDuration = 0;



//----------------------------------


// Declaring variable to store LED instructions.
byte instructions = 0;

// Selecting the pins for the LED (green)
// Todo: Set the right pin number for the green and red LED.
const int LED_GREEN = 11;
const int LED_RED = 13;
const int LED_YELLOW = 12;
const int BUTTON = 3;

int buttonState = 0;
int last_state = 0;
//const int LED_BLUE = 8;

// This method sends measurements to the Raspberry pi over the serial 
// connection. The Raspberry pi assumes that the sign + or - is sent and that
// the mesurement has two digits and two decimals.
//
// Consult the following sites to solve this task:
// Serial: https://www.arduino.cc/reference/en/language/functions/communication/serial/print
void printButton(int value)
{
  if (last_state == value) return;
  last_state = value;
  if (value == 1)
    Serial.write('1');
  else
    Serial.write('0');
}

// This method reads instructions from the serial bus and sets the LED-diods
// to low or high depending on the instructions. The instructions are two bytes.
//
// Serial: https://www.arduino.cc/reference/en/language/functions/communication/serial/print
void updateLEDs()
{
    while(Serial.available()>=1)
  {
	  // Todo: Read one byte from the serial bus into the instructions 
	  //       variable.
    Serial.readBytes(&instructions,1);
    Serial.flush();

  }
  
  //if(instructions[0] == 1) {
  //  digitalWrite(LED_BLUE, HIGH);
  //}

  // Sets the green LED to high if the first bit in the instructions variable
  // is a 1 and sets the green LED to low if the first bit of the instructions
  // variable is 0.
  
  // Todo: Set the green LED to low/high depending on the first bit of the 
  //       instructions variable.
  
  if ((instructions & 2)>>1 == 1){
    if((instructions & 1)  == 1) {
      digitalWrite(LED_GREEN, HIGH);
    } else {
      digitalWrite(LED_GREEN, LOW);
    }
  }

  if ((instructions & 8)>>3 == 1){
    if(((instructions & 4)>>2) == 1) {
      digitalWrite(LED_YELLOW, HIGH);
    } else {
      digitalWrite(LED_YELLOW, LOW);
    }
  }
  if ((instructions & 32)>>5 == 1){
    if(((instructions & 16)>>4) == 1) {
      digitalWrite(LED_RED, HIGH);
    } else {
      digitalWrite(LED_RED, LOW);
    }
  }

  if ((instructions & 128)>>7 == 1){
    if ((instructions & 64)>>6 == 1){
      for (int thisNote = 0; thisNote < notes_win * 2; thisNote = thisNote + 2) {

      // calculates the duration of each note
      divider = melody_win[thisNote + 1];
      if (divider > 0) {
        // regular note, just proceed
        noteDuration = (wholenote) / divider;
      } else if (divider < 0) {
        // dotted notes are represented with negative durations!!
        noteDuration = (wholenote) / abs(divider);
        noteDuration *= 1.5; // increases the duration in half for dotted notes
      }
  
      // we only play the note for 90% of the duration, leaving 10% as a pause
      tone(buzzer, melody_win[thisNote], noteDuration*0.9);

      // Wait for the specief duration before playing the next note.
      delay(noteDuration);
    
      // stop the waveform generation before the next note.
      noTone(buzzer);
      }
    }
    else {
      for (int thisNote = 0; thisNote < notes_lose * 2; thisNote = thisNote + 2) {

      // calculates the duration of each note
      divider = melody_lose[thisNote + 1];
      if (divider > 0) {
        // regular note, just proceed
        noteDuration = (wholenote) / divider;
      } else if (divider < 0) {
        // dotted notes are represented with negative durations!!
        noteDuration = (wholenote) / abs(divider);
        noteDuration *= 1.5; // increases the duration in half for dotted notes
      }
  
      // we only play the note for 90% of the duration, leaving 10% as a pause
      tone(buzzer, melody_lose[thisNote], noteDuration*0.9);

      // Wait for the specief duration before playing the next note.
      delay(noteDuration);
    
      // stop the waveform generation before the next note.
      noTone(buzzer);
      }     
    }
  }
  instructions = 0;
}

void setup() {
  // Setup for that runs once in the beginning.
  // Defining the type of pins, in this case output.
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW,OUTPUT);
  pinMode(BUTTON,INPUT);

  // Starting a serial connection.
  Serial.begin(9600);  
  delay(2000);
  
}

// This is the main loop of the Arduino code. 
void loop() 
{
  // Reading the instructions from the serial bus.
    updateLEDs();
    buttonState = digitalRead(BUTTON);
    printButton(buttonState);
}
