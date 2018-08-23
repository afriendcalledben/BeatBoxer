#include <bitswap.h>
#include <chipsets.h>
#include <color.h>
#include <colorpalettes.h>
#include <colorutils.h>
#include <controller.h>
#include <cpp_compat.h>
#include <dmx.h>
#include <FastLED.h>
#include <fastled_config.h>
#include <fastled_delay.h>
#include <fastled_progmem.h>
#include <fastpin.h>
#include <fastspi.h>
#include <fastspi_bitbang.h>
#include <fastspi_dma.h>
#include <fastspi_nop.h>
#include <fastspi_ref.h>
#include <fastspi_types.h>
#include <hsv2rgb.h>
#include <led_sysdefs.h>
#include <lib8tion.h>
#include <noise.h>
#include <pixelset.h>
#include <pixeltypes.h>
#include <platforms.h>
#include <power_mgt.h>

// Punch Glove 

#define NUM_STREAM_LEDS 40 
#define DATA_PIN 6 
#define PIEZO_PIN A0

CRGB streamLEDS[NUM_STREAM_LEDS];
int streamLEDValues[NUM_STREAM_LEDS];
long piezoValue = 0.0;

long punchExpectedTime = 0;
long punchDeliveredTime = 0;
int punchStart = 0;

int lastPunchColor = 0;
int lastPunchValue = 0;

long prevLoopMillis = 0;
long previousMillis = 0;
long interval = 30;

long punchAfterTimer = 0;

int incomingByte = 0;

int gameState = 0;

void setup() {
  // Set up the NeoPixel strip
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(streamLEDS, NUM_STREAM_LEDS);
  // Set all color values to 0
  for (int i = 0; i < NUM_STREAM_LEDS; i++)
  {
    streamLEDValues[i] = 0;
  }
  // Open serial connection
  Serial.begin(9600);
}

void loop() {
  unsigned long currentMillis = millis();

  // Process these functions every 30 milliseconds
  if (currentMillis - previousMillis > interval) {
    movePulse(); // Move pulse lights along
    processPunch(); // Process any delivered punches
    renderLights(); // Render the colour of all lights
    previousMillis = currentMillis;
  }

  // Read the vibration from the Piezo sensor 
  int piezoADC = analogRead(PIEZO_PIN);
  float piezoV = piezoADC / 1023.0 * 5.0 * 10000.0;
  // If the vibration is larger than the last recorded value, replace it to acertain the highest vibration.
  // Or else, reduce the recorded vibration level by half.
  if (piezoV > piezoValue)
  {
    piezoValue = piezoV;
  } else {
    piezoValue /= 2;
  }
  // If the highest recorded vibration value is over 3000, recognise it as a punch
  if (piezoValue > 3000) {
    // If the punch process hasn't begun yet, record when the punch was delivered.
    if (punchStart == 0) {
      punchDelivered();
      punchStart = 1;
      lastPunchValue = piezoValue - 3000;
    }
    // If the punch process has begun, wait until the vibration level has begun falling to register the highest punch value;
    if (punchStart == 1) {
      if (piezoValue < lastPunchValue)
      {
        // Process punch with the highest vibration value;
        punchProcessed(lastPunchValue);
        punchAfterTimer =  currentMillis;
        punchStart = 2;
      }
      lastPunchValue = piezoValue;
    }
    if (punchStart == 2)
    {
      // Wait half a second after a punch to allow to accept a new punch
      if (currentMillis - punchAfterTimer >= 500)
      {
        punchStart = 0;
      }
    }
  }

  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte == 97) {
      gameState = 0;
    } else if (incomingByte == 98) {
      gameState = 1;
    } else if (incomingByte == 99) {
      streamLEDValues[39] = 1;
      renderLights();
    }
  }
  prevLoopMillis = currentMillis;
}

void punchExpected(int offset = 0)
{
  punchExpectedTime = millis() + offset;
}

void movePulse()
{
  // For NeoPixels assigned to the arm trails...
  for (int i = 20; i < 40; i++)
  {
    // If the Color value of the LED more than black
    if (streamLEDValues[i] > 0) {
      if (i > 20) {
        streamLEDValues[i - 1] = streamLEDValues[i];
        if (i > 15 && streamLEDValues[i - 1] > 0) {
          punchExpected(((39 - i) * 30) + ((39 - i) * 1));
        }
      } else {
        punchExpected(0);
      }
      streamLEDValues[i] = 0;
    }
  }
}

void processPunch()
{

  if (millis() - punchDeliveredTime > 500) {
    for (int i = 0; i < 10; i++)
    {
      if (streamLEDValues[i] > 0)
      {
        streamLEDValues[i] = 0;
        streamLEDValues[19-i] = 0;
        break;
      }
    }
  }
}

void punchDelivered()
{
  if (gameState > 0) {
    int difference = -1;
    punchDeliveredTime = millis();
    difference = abs(punchDeliveredTime - punchExpectedTime);
    if (difference >= 0) {
      lastPunchValue = 20 / 120 * (120 - difference);
      lastPunchColor = 0;
      if (difference < 20) {
        Serial.print("1");
        lastPunchColor = 1;
      } else if (difference < 60) {
        Serial.print("2");
        lastPunchColor = 2;
      } else if (difference < 120) {
        Serial.print("3");
        lastPunchColor = 3;
      } else if (difference < 500) {
        Serial.print("4");
        lastPunchColor = 4;
      } else {
        Serial.print("5");
        lastPunchColor = 5;
      }
    }
  } else {
    lastPunchColor = 6;
    Serial.print("*");
  }
}

void punchProcessed(int power)
{
  if (lastPunchColor > 0) {
    if (lastPunchColor == 5) {
      for (int i = 5; i < 15; i++)
      {
        streamLEDValues[i] = lastPunchColor;
      }
    } else {
      for (int i = 0; i < 20; i++)
      {
        streamLEDValues[i] = lastPunchColor;
      }
    }
  }
}

void renderLights()
{
  for (int i = 20; i < 40; i++)
  {
    if (streamLEDValues[i] > 0) {
      switch (streamLEDValues[i]) {
        case 1:
          streamLEDS[i] = CRGB::White;
          break;
        case 2:
          streamLEDS[i] = CRGB::Green;
          break;
        case 3:
          streamLEDS[i] = CRGB::Yellow;
          break;
        case 4:
          streamLEDS[i] = CRGB::Tomato;
          break;
        case 5:
          streamLEDS[i] = CRGB::Red;
          break;
      }
    } else {
      CRGB currLED = streamLEDS[i];
      streamLEDS[i] = CRGB(currLED.r / 2, currLED.b / 2, currLED.b / 2);
    }
  }
  for (int i = 0; i < 20; i++)
  {
    if (streamLEDValues[i] > 0) {
      switch (streamLEDValues[i]) {
        case 1:
          streamLEDS[i] = CRGB::Green; // BEST
          break;
        case 2:
          streamLEDS[i] = CRGB::Yellow; // GOOD
          break;
        case 3:
          streamLEDS[i] = CRGB::Turquoise; // OK
          break;
        case 4:
          streamLEDS[i] = CRGB::Purple; // BAD
          break;
        case 5:
          streamLEDS[i] = CRGB::Red; // MISS
          break;
        case 6:
          streamLEDS[i] = CRGB::White;
          break;
      }
    } else {
      streamLEDS[i] = CRGB::Black;
    }
  }
  FastLED.show();
}

