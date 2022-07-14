#ifndef DistanceDetector_driver_h
#define DistanceDetector_driver_h

#include <Arduino.h>

class DistanceDetectorDriver{
    private:
        byte distanceEchoPin;
        byte distanceTriggerPin;

    public:
        DistanceDetectorDriver(byte distanceEchoPin, byte distanceTriggerPin);

        void detectDistance();

};


#endif