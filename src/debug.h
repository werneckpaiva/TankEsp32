#ifndef debug_h
#define debug_h

#include <Arduino.h>

#define DEBUG_MODE

class Debug {
    public:
        static 
}

void debug(const char *msg, ...){

    Serial.print(msg);

}

#endif