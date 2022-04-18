#ifndef LightsStrip_driver_h
#define LightsStrip_driver_h

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

class LightsStripDriver{
    private:
        byte numPixels;
        Adafruit_NeoPixel *pixels;
        
    public:
        static constexpr const byte BLACK[]     = {0, 0, 0};
        static constexpr const byte LILAC[]     = {148, 0, 211};
        static constexpr const byte PURPLE[]    = {75, 0, 130};
        static constexpr const byte BLUE[]      = {0, 0, 255};
        static constexpr const byte GREEN[]     = {0, 255, 0};
        static constexpr const byte YELLOW[]    = {255, 255, 0};
        static constexpr const byte ORANGE[]    = {255, 127, 0};
        static constexpr const byte RED[]       = {255, 0, 0};
        static constexpr const byte WHITE[]     = {255, 255, 255};

        LightsStripDriver(uint16_t numPixels, int16_t ledStripPin);

        void showPixel(byte x, byte r, byte g, byte b, float brightness);

        void showPixel(byte x, const byte *color, float brightness);

        void paint(const byte *color, byte posInit, byte posEnd, float brightness=0.2);

        void fullPaint(const byte *color, float brightness);

        void clear();

        void show();
};

constexpr byte LightsStripDriver::BLACK[];
constexpr byte LightsStripDriver::LILAC[];
constexpr byte LightsStripDriver::PURPLE[];
constexpr byte LightsStripDriver::BLUE[];
constexpr byte LightsStripDriver::GREEN[];
constexpr byte LightsStripDriver::YELLOW[];
constexpr byte LightsStripDriver::ORANGE[];
constexpr byte LightsStripDriver::RED[];
constexpr byte LightsStripDriver::WHITE[];


LightsStripDriver::LightsStripDriver(uint16_t numPixels, int16_t ledStripPin){
    this->numPixels = numPixels;
    this->pixels = new Adafruit_NeoPixel(numPixels, ledStripPin, NEO_GRB + NEO_KHZ800);
    this->pixels->begin();
}

void LightsStripDriver::showPixel(byte x, byte r, byte g, byte b, float brightness){
    byte red = r * brightness;
    byte green = g * brightness;
    byte blue = b * brightness;
    this->pixels->setPixelColor(x, this->pixels->Color(red, green, blue));
}

void LightsStripDriver::showPixel(byte x, const byte *color, float brightness){
    this->showPixel(x, color[0], color[1], color[2], brightness);
}

void LightsStripDriver::paint(const byte *color, byte posInit, byte posEnd, float brightness){
    for (byte i=posInit; i<=posEnd; i++){
        this->showPixel(i, color[0], color[1], color[2], brightness);
    }
}

void LightsStripDriver::fullPaint(const byte* color, float brightness){
    this->pixels->clear();
    this->paint(color, 0, 7, brightness);
    this->pixels->show();
}

void LightsStripDriver::clear(){
    this->pixels->clear();
    this->pixels->show();
}

void LightsStripDriver::show(){
    this->pixels->show();
}


#endif