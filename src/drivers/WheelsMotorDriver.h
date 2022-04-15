#ifndef WheelsMotor_driver_h
#define WheelsMotor_driver_h

#include <Arduino.h>

class WheelsMotorDriver{
    private:
        const byte PWM_RESOLUTION = 8; // 8 bits = 0-256
        
        byte m1a_pin;
        byte m1b_pin;
        byte m2a_pin;
        byte m2b_pin;

        const byte m1a_ch = 0;
        const byte m1b_ch = 1;
        const byte m2a_ch = 2;
        const byte m2b_ch = 3;

    public:
        WheelsMotorDriver(byte m1a_pin, byte m1b_pin, byte m2a_pin, byte m2b_pin);
        void moveForward(byte vel);
        void moveBackward(byte vel);
        void spinRight(byte vel);
        void spinLeft(byte vel);
        void stopMoving();
        void turn(int vertVel, int horizVel);
};

WheelsMotorDriver::WheelsMotorDriver(byte m1a_pin, byte m1b_pin, byte m2a_pin, byte m2b_pin){
    this->m1a_pin = m1a_pin;
    this->m1b_pin = m1b_pin;
    this->m2a_pin = m2a_pin;
    this->m2b_pin = m2b_pin;

    ledcAttachPin(m1a_pin, m1a_ch);
    ledcSetup(m1a_ch, 1000, 8);
    ledcAttachPin(m1b_pin, 1);
    ledcSetup(m1b_ch, 1000, 8);
    ledcAttachPin(m2a_pin, 2);
    ledcSetup(m2a_ch, 1000, 8);
    ledcAttachPin(m2b_pin, 3);
    ledcSetup(m2b_ch, 1000, 8);
}

void WheelsMotorDriver::moveForward(byte vel){
    ledcWrite(this->m1a_ch, vel);
    ledcWrite(this->m1b_ch, 0);
    ledcWrite(this->m2a_ch, vel);
    ledcWrite(this->m2b_ch, 0);  
}

void WheelsMotorDriver::moveBackward(byte vel){
    ledcWrite(this->m1a_ch, 0);
    ledcWrite(this->m1b_ch, vel);
    ledcWrite(this->m2a_ch, 0);
    ledcWrite(this->m2b_ch, vel);
}

void WheelsMotorDriver::spinRight(byte vel){
    ledcWrite(this->m1a_ch, 0);
    ledcWrite(this->m1b_ch, vel);
    ledcWrite(this->m2a_ch, vel);
    ledcWrite(this->m2b_ch, 0);
}

void WheelsMotorDriver::spinLeft(byte vel){
    ledcWrite(this->m1a_ch, vel);
    ledcWrite(this->m1b_ch, 0);
    ledcWrite(this->m2a_ch, 0);
    ledcWrite(this->m2b_ch, vel);
}

void WheelsMotorDriver::stopMoving(){
    ledcWrite(this->m1a_ch, 0);
    ledcWrite(this->m1b_ch, 0);
    ledcWrite(this->m2a_ch, 0);
    ledcWrite(this->m2b_ch, 0);
}


#endif