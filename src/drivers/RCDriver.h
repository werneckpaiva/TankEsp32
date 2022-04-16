#ifndef RC_driver_h
#define RC_driver_h

#include <Arduino.h>
#include <IBusBM.h>

class RCDriver{
    private:;
        IBusBM ibusRc;
    public:
        RCDriver(HardwareSerial &ibusRcSerial);
        int readChannel(byte channelInput, int minLimit, int maxLimit, int defaultValue);
        bool redSwitch(byte channelInput, bool defaultValue);

};

RCDriver::RCDriver(HardwareSerial &ibusRcSerial){
    this->ibusRc.begin(ibusRcSerial, 1);
}

// Read the number of a given channel and convert to the range provided.
// If the channel is off, return the default value
int RCDriver::readChannel(byte channelInput, int minLimit, int maxLimit, int defaultValue) {
  uint16_t ch = this->ibusRc.readChannel(channelInput);
  if (ch < 100 or ch > 2500) return defaultValue;
  return map(ch, 1000, 2000, minLimit, maxLimit);
}

// Red the channel and return a boolean value
bool RCDriver::redSwitch(byte channelInput, bool defaultValue) {
  int intDefaultValue = (defaultValue) ? 100 : 0;
  int ch = readChannel(channelInput, 0, 100, intDefaultValue);
  return (ch > 50);
}

#endif