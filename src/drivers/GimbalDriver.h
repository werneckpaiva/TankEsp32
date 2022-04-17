#ifndef Gimbal_driver_h
#define Gimbal_driver_h

#include <Arduino.h>
#include <ESP32Servo.h>

class GimbalDriver{
    private:
        Servo servoHorz; 
        Servo servoVert; 

    public:
        GimbalDriver(byte servoHorzPin , byte servoVertPin);
        // Horizontal movement
        void pan(byte angle);
        // Vertical movement
        void tilt(byte angle);
};

GimbalDriver::GimbalDriver(byte servoHorzPin , byte servoVertPin){
    ESP32PWM::allocateTimer(4);
    ESP32PWM::allocateTimer(5);

    this->servoHorz.setPeriodHertz(50);
    this->servoHorz.attach(servoHorzPin, 500, 2400);

    this->servoVert.setPeriodHertz(50);
    this->servoVert.attach(servoVertPin, 500, 2400);
};

void GimbalDriver::pan(byte angle){
    this->servoHorz.write(angle);
};

void GimbalDriver::tilt(byte angle){
    this->servoVert.write(angle);
};


#endif