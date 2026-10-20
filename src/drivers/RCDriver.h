#ifndef RC_driver_h
#define RC_driver_h

#include <Arduino.h>
#include <IBusBM.h>

class RCDriver{
    private:
        // iBus channel values are pulse widths in microseconds
        static const uint16_t PULSE_MIN_US = 1000;
        static const uint16_t PULSE_MAX_US = 2000;
        // Values outside this range mean the channel is off or there is no signal
        static const uint16_t VALID_MIN_US = 100;
        static const uint16_t VALID_MAX_US = 2500;
        static const int8_t IBUS_TIMER_ID = 1;

        IBusBM ibusRc;
    public:
        RCDriver(HardwareSerial &ibusRcSerial);
        int readChannel(byte channelInput, int minLimit, int maxLimit, int defaultValue);
        bool readSwitch(byte channelInput, bool defaultValue);

};

RCDriver::RCDriver(HardwareSerial &ibusRcSerial){
    this->ibusRc.begin(ibusRcSerial, IBUS_TIMER_ID);
}

// Read a channel and map it to the range [minLimit, maxLimit].
// If the channel is off, return the default value.
int RCDriver::readChannel(byte channelInput, int minLimit, int maxLimit, int defaultValue) {
  uint16_t pulse = this->ibusRc.readChannel(channelInput);
  // DEBUG_PRINTF("ch-%d: %d\n", channelInput, pulse);
  if (pulse < VALID_MIN_US or pulse > VALID_MAX_US) return defaultValue;
  return map(pulse, PULSE_MIN_US, PULSE_MAX_US, minLimit, maxLimit);
}

// Read a channel as an on/off switch: on above the middle of its range
bool RCDriver::readSwitch(byte channelInput, bool defaultValue) {
  int intDefaultValue = (defaultValue) ? 100 : 0;
  int percent = readChannel(channelInput, 0, 100, intDefaultValue);
  return (percent > 50);
}

#endif
