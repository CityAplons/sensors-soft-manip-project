// This code is intended for data handling, correction and sending, run on ESP32 WROOM dev kit v1
// Libraries for SD card
#include <FS.h>
#include <FSImpl.h>
#include <vfs_api.h>
#include <SD.h>
#include <SPI.h>

// Library for LED
#include <FastLED.h>

// Websockets libraries
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <WebSocketsServer.h>

#define NUM_LEDS 6        // Number of LED in the stripe
#define PIN_FSR_1 34      
#define PIN_FSL_1 35
#define PIN_FSR_2 32
#define PIN_FSL_2 33
#define PIN_FSR_3 14
#define PIN_FSL_3 12
#define PIN_LED_FIRST 26
#define PIN_LED_SECOND 27
#define PIN_LED_THIRD 25
#define SD_CS     5        // Define CS pin for the SD card module

CRGB leds_1[NUM_LEDS];
CRGB leds_2[NUM_LEDS];
CRGB leds_3[NUM_LEDS];
String dataMessage;
char* filename = "/data_free_displacement.txt";
unsigned long int readingID = 0;
unsigned long int _time;  // Seconds
byte counter;
int FSL_1_reading;
int FSL_2_reading;
int FSL_3_reading;
int FSR_1_reading;
int FSR_2_reading;
int FSR_3_reading;
int FSR_max;
int FSL_avg;
int hue;
int F;

const char *ssid = "MGTS_GPON_8E38";
const char *password =  "NxpNRAXG";
// WebSocket globals
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");
AsyncEventSource events("/events");

// Callback: receiving any WebSocket message
void onWebSocketEvent(AsyncWebSocket * server, AsyncWebSocketClient * client, AwsEventType type, void * arg, uint8_t *payload, size_t len) {

  // Figure out the type of WebSocket event
  switch(type) {

    // Client has disconnected
    case WStype_DISCONNECTED:
      Serial.printf("[%u] Disconnected!\n", client->id());
      break;

    // New client has connected
    case WStype_CONNECTED:
      {
        Serial.printf("[%u] Connection from ", client->id());
      }
      break;
    // For everything else: do nothing
    case WStype_TEXT:
    case WStype_BIN:
    case WStype_ERROR:
    case WStype_FRAGMENT_TEXT_START:
    case WStype_FRAGMENT_BIN_START:
    case WStype_FRAGMENT:
    case WStype_FRAGMENT_FIN:
    default:
      break;
  }
}

void setup() {
  // initialize serial communication at 9600 bits per second:
  FastLED.addLeds<WS2811, PIN_LED_FIRST, GRB>(leds_1, NUM_LEDS).setCorrection( TypicalLEDStrip );
  FastLED.addLeds<WS2811, PIN_LED_SECOND, GRB>(leds_2, NUM_LEDS).setCorrection( TypicalLEDStrip );
  FastLED.addLeds<WS2811, PIN_LED_THIRD, GRB>(leds_3, NUM_LEDS).setCorrection( TypicalLEDStrip );
  FastLED.setBrightness(150);
  Serial.begin(9600);
  
  // Initialize SD card
  SD.begin(SD_CS);  
  if(!SD.begin(SD_CS)) {
    Serial.println("Card Mount Failed");
    return;
  }
  uint8_t cardType = SD.cardType();
  if(cardType == CARD_NONE) {
    Serial.println("No SD card attached");
    return;
  }
  Serial.println("Initializing SD card...");
  if (!SD.begin(SD_CS)) {
    Serial.println("ERROR - SD card initialization failed!");
    return;    // init failed
  }
  // If the data.txt file doesn't exist
  // Create a file on the SD card and write the data labels
  File file = SD.open(filename);
  if(!file) {
    Serial.println("File doens't exist");
    Serial.println("Creating file...");
    writeFile(SD, filename, "ReadingID, time, fsr1, fsr2, fsr3, fsl1, fsl2, fsl3, fsr_max, fsl_avg, hue, force \r\n");
  }
  else {
    Serial.println("File already exists, remove, create new");
    SD.remove(filename);
    writeFile(SD, filename, "Start a new data harvesting... \r\n"); 
    writeFile(SD, filename, "ReadingID, time, fsr1, fsr2, fsr3, fsl1, fsl2, fsl3, fsr_max, fsl_avg, hue, force \r\n");
  }
  file.close();

  // Setting up WiFi server
  WiFi.begin(ssid, password);
  Serial.print("Connecting to ");
  Serial.print(ssid); Serial.println(" ...");
  while (WiFi.status() != WL_CONNECTED) { // Wait for the Wi-Fi to connect
    delay(1000);
    Serial.print('.');
  }
  Serial.println('\n');
  Serial.println("Connection established!");  
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
      request->send(200, "text/plain", "Welcome. WebSocket server located on route /ws");
  });

  server.onNotFound([](AsyncWebServerRequest *request){
    request->send(404, "text/plain", "Not found");  
  });
    
  ws.onEvent(onWebSocketEvent);
  server.addHandler(&ws);

  server.begin();
}
int max3(int a, int b, int c)
{
  int maxguess;
  maxguess = max(a,b);  // biggest of A and B
  maxguess = max(maxguess, c);  // but maybe C is bigger?

  return(maxguess);
}
// the loop routine runs over and over again forever:
void loop() {
  _time = millis();
  FSL_1_reading = analogRead(PIN_FSL_1);
  FSR_1_reading = analogRead(PIN_FSR_1);
  FSL_2_reading = analogRead(PIN_FSL_2);
  FSR_2_reading = analogRead(PIN_FSR_2);
  FSL_3_reading = analogRead(PIN_FSL_3);
  FSR_3_reading = analogRead(PIN_FSR_3);
  FSR_max = max3(FSR_1_reading, FSR_2_reading, FSR_3_reading);
  FSL_avg = int((FSL_1_reading + FSL_2_reading + FSL_3_reading)/3);
  int hue_max = 210;
  int hue_min = 45;
  FSR_max = map(FSR_max, 5, 2400, hue_min, hue_max);
  FSL_avg = map(FSL_avg, 950, 1150, hue_min, hue_max);
  FSR_max = constrain(FSR_max, hue_min, hue_max);
  FSL_avg = constrain(FSL_avg, hue_min, hue_max);
  // setting up color of each actuator
  hue = int((FSR_max + FSL_avg)/2);
  // force estimation
  F = map(hue, hue_min, hue_max, 0, 100);

  for (int i = 0; i < NUM_LEDS; i++ ) {         // от 0 до первой трети
    leds_1[i] = CHSV(255-hue, 255, 255);  // HSV. Увеличивать HUE (цвет)
    leds_2[i] = CHSV(255-hue, 255, 255);
    leds_3[i] = CHSV(255-hue, 255, 255);
    
    // умножение i уменьшает шаг радуги
  }
  counter++;        // counter меняется от 0 до 255 (тип данных byte)
  FastLED.show();
  delay(5);         // скорость движения радуги

  Serial.print("ID: ");
  Serial.print(readingID);
  Serial.print("\t");
  Serial.print("time: ");
  Serial.print(_time);
  Serial.print("\t");
  Serial.print("Force 1: ");
  Serial.print(FSR_1_reading);
  Serial.print("\t");
  Serial.print("Flex 1: ");
  Serial.print(FSL_1_reading);
  Serial.print("\t");
  Serial.print("Force 2: ");
  Serial.print(FSR_2_reading);
  Serial.print("\t");
  Serial.print("Flex 2: ");
  Serial.print(FSL_2_reading);
  Serial.print("\t");
  Serial.print("Force 3: ");
  Serial.print(FSR_3_reading);
  Serial.print("\t");
  Serial.print("Flex 3: ");
  Serial.print(FSL_3_reading);
  Serial.print("\t");
  Serial.print("FSR_max: ");
  Serial.print(FSR_max);
  Serial.print("\t");
  Serial.print("FSL_avg: ");
  Serial.print(FSL_avg);
  Serial.print("\t");
  Serial.print("hue: ");
  Serial.println(hue);

  //logSDCard();
  readingID++;

  //Sending information for all websocket users
  ws.textAll(String(FSR_max) + "," + String(FSL_avg)+ "," + String(hue));
  
  // Refreshing user list (connect/disconnect)
  ws.cleanupClients();
}

// Write the sensor readings on the SD card
void logSDCard() {
  dataMessage = String(readingID) + "," + String(_time)+ "," + String(FSR_1_reading) + "," + String(FSR_2_reading) + "," + String(FSR_3_reading) + ","
                + String(FSL_1_reading) + "," + String(FSL_2_reading) + "," + String(FSL_3_reading) + "," + String(FSR_max) + "," + String(FSL_avg) + "," + String(hue) + "," + String(F) + "\r\n";
  Serial.print("\t");
  Serial.print("Save data: ");
  Serial.println(dataMessage);
  appendFile(SD, filename, dataMessage.c_str());
}
 
// Write to the SD card (DON'T MODIFY THIS FUNCTION)
void writeFile(fs::FS &fs, const char * path, const char * message) {
//  Serial.printf("Writing file: %s\n", path);
 
  File file = fs.open(path, FILE_WRITE);
  if(!file) {
    Serial.println("Failed to open file for writing");
    return;
  }
  if(file.print(message)) {
//    Serial.println("File written");
  } else {
    Serial.println("Write failed");
  }
  file.close();
}
 
// Append data to the SD card (DON'T MODIFY THIS FUNCTION)
void appendFile(fs::FS &fs, const char * path, const char * message) {
//  Serial.printf("Appending to file: %s\n", path);
 
  File file = fs.open(path, FILE_APPEND);
  if(!file) {
    Serial.println("Failed to open file for appending");
    return;
  }
  if(file.print(message)) {
//   Serial.println("Message appended");
  } else {
    Serial.println("Append failed");
  }
  file.close();
}
