#ifndef WheelsMotor_driver_h
#define WheelsMotor_driver_h

#include <Arduino.h>

class WheelsMotorDriver{
    private:
        const byte PWM_RESOLUTION = 8; // bits
        const unsigned int PWM_FREQUENCY = 1000;  // hz

        byte m1aPin;
        byte m1bPin;
        byte m2aPin;
        byte m2bPin;

        const byte m1aChannel = 0;
        const byte m1bChannel = 1;
        const byte m2aChannel = 2;
        const byte m2bChannel = 3;

    public:
        WheelsMotorDriver(byte m1aPin, byte m1bPin, byte m2aPin, byte m2bPin);
        void moveForward(int horizSpeed, int vertSpeed);
        void moveBackward(int horizSpeed, int vertSpeed);
        void spinRight(int vel);
        void spinLeft(int vel);
        void stopMoving();
        void turn(int vertVel, int horizVel);
};

WheelsMotorDriver::WheelsMotorDriver(byte m1aPin, byte m1bPin, byte m2aPin, byte m2bPin){
    this->m1aPin = m1aPin;
    this->m1bPin = m1bPin;
    this->m2aPin = m2aPin;
    this->m2bPin = m2bPin;

    ledcAttachPin(m1aPin, m1aChannel);
    ledcSetup(m1aChannel, PWM_FREQUENCY, PWM_RESOLUTION);
    ledcAttachPin(m1bPin, m1bChannel);
    ledcSetup(m1bChannel, PWM_FREQUENCY, PWM_RESOLUTION);
    ledcAttachPin(m2aPin, m2aChannel);
    ledcSetup(m2aChannel, PWM_FREQUENCY, PWM_RESOLUTION);
    ledcAttachPin(m2bPin, m2bChannel);
    ledcSetup(m2bChannel, PWM_FREQUENCY, PWM_RESOLUTION);
}

void WheelsMotorDriver::moveForward(int horizSpeed, int vertSpeed){
    int speedMotorLeft = vertSpeed;
    int speedMotorRight = vertSpeed;
    if (horizSpeed < 0) {
        speedMotorLeft *= (255.0 + horizSpeed) / 255;
    } else if (horizSpeed > 0) {
        speedMotorRight *= (255.0 - horizSpeed) / 255;
    }
    ledcWrite(this->m1aChannel, 0);
    ledcWrite(this->m1bChannel, speedMotorLeft);
    ledcWrite(this->m2aChannel, 0);
    ledcWrite(this->m2bChannel, speedMotorRight);  
}

void WheelsMotorDriver::moveBackward(int horizSpeed, int vertSpeed){
    int speedMotorLeft = -1 * vertSpeed;
    int speedMotorRight = -1 * vertSpeed;
    if (horizSpeed < -5) {
        speedMotorLeft *= (255.0 + horizSpeed) / 255;
    } else if (horizSpeed > 5) {
        speedMotorRight *= (255.0 - horizSpeed) / 255;
    }
    ledcWrite(this->m1aChannel, speedMotorLeft);
    ledcWrite(this->m1bChannel, 0);
    ledcWrite(this->m2aChannel, speedMotorRight);
    ledcWrite(this->m2bChannel, 0);
}

void WheelsMotorDriver::spinRight(int vel){
    ledcWrite(this->m1aChannel, vel);
    ledcWrite(this->m1bChannel, 0);
    ledcWrite(this->m2aChannel, 0);
    ledcWrite(this->m2bChannel, vel);
}

void WheelsMotorDriver::spinLeft(int vel){
    vel *= -1;
    ledcWrite(this->m1aChannel, 0);
    ledcWrite(this->m1bChannel, vel);
    ledcWrite(this->m2aChannel, vel);
    ledcWrite(this->m2bChannel, 0);
}

void WheelsMotorDriver::stopMoving(){
    ledcWrite(this->m1aChannel, 0);
    ledcWrite(this->m1bChannel, 0);
    ledcWrite(this->m2aChannel, 0);
    ledcWrite(this->m2bChannel, 0);
}


#endif