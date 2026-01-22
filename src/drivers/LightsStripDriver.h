#ifndef LightsStrip_driver_h
#define LightsStrip_driver_h

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>


class LightsStripDriver {
private:
  byte numPixels;
  Adafruit_NeoPixel *pixels;

public:
  static const byte *BLACK() {
    static const byte c[] = {0, 0, 0};
    return c;
  }
  static const byte *LILAC() {
    static const byte c[] = {148, 0, 211};
    return c;
  }
  static const byte *PURPLE() {
    static const byte c[] = {75, 0, 130};
    return c;
  }
  static const byte *BLUE() {
    static const byte c[] = {0, 0, 255};
    return c;
  }
  static const byte *GREEN() {
    static const byte c[] = {0, 255, 0};
    return c;
  }
  static const byte *YELLOW() {
    static const byte c[] = {255, 255, 0};
    return c;
  }
  static const byte *ORANGE() {
    static const byte c[] = {255, 127, 0};
    return c;
  }
  static const byte *RED() {
    static const byte c[] = {255, 0, 0};
    return c;
  }
  static const byte *WHITE() {
    static const byte c[] = {255, 255, 255};
    return c;
  }

  LightsStripDriver(uint16_t numPixels, int16_t ledStripPin);

  void showPixel(byte x, byte r, byte g, byte b, float brightness);

  void showPixel(byte x, const byte *color, float brightness);

  void paint(const byte *color, byte posInit, byte posEnd,
             float brightness = 0.2);

  void fullPaint(const byte *color, float brightness);

  void clear();

  void show();
};

LightsStripDriver::LightsStripDriver(uint16_t numPixels, int16_t ledStripPin) {
  this->numPixels = numPixels;
  this->pixels = new Adafruit_NeoPixel(numPixels, ledStripPin, NEO_GRB + NEO_KHZ800);
  this->pixels->begin();
}

void LightsStripDriver::showPixel(byte x, byte r, byte g, byte b, float brightness) {
  byte red = r * brightness;
  byte green = g * brightness;
  byte blue = b * brightness;
  this->pixels->setPixelColor(x, this->pixels->Color(red, green, blue));
}

void LightsStripDriver::showPixel(byte x, const byte *color, float brightness) {
  this->showPixel(x, color[0], color[1], color[2], brightness);
}

void LightsStripDriver::paint(const byte *color, byte posInit, byte posEnd, float brightness) {
  for (byte i = posInit; i <= posEnd; i++) {
    this->showPixel(i, color[0], color[1], color[2], brightness);
  }
}

void LightsStripDriver::fullPaint(const byte *color, float brightness) {
  Serial.println("LightsStripDriver: fullPaint");
  Serial.printf("Color: R=%d G=%d B=%d Brightness=%.2f\n", color[0], color[1], color[2], brightness);
  this->pixels->clear();
  this->paint(color, 0, 7, brightness);
  this->pixels->show();
  Serial.println("LightsStripDriver: fullPaint done");
}

void LightsStripDriver::clear() {
  this->pixels->clear();
  this->pixels->show();
}

void LightsStripDriver::show() {
  this->pixels->show();
}

#endif