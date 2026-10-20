#ifndef WheelsMotor_driver_h
#define WheelsMotor_driver_h

#include <Arduino.h>

/*
 * Drives the two tracks through an H-bridge: motor 1 is the left track and
 * motor 2 the right one. Each motor has an A and a B input; PWM on B drives
 * it forward, PWM on A backward. Speeds are PWM duties 0..255.
 */
class WheelsMotorDriver{
    private:
        const byte PWM_RESOLUTION = 8; // bits
        const unsigned int PWM_FREQUENCY = 1000;  // hz

        byte m1aPin;
        byte m1bPin;
        byte m2aPin;
        byte m2bPin;

        const byte m1aChannel = 10;
        const byte m1bChannel = 11;
        const byte m2aChannel = 12;
        const byte m2bChannel = 13;

    public:
        WheelsMotorDriver(byte m1aPin, byte m1bPin, byte m2aPin, byte m2bPin);
        // vertSpeed > 0; horizSpeed < 0 slows the left track, > 0 the right one
        void moveForward(int horizSpeed, int vertSpeed);
        // vertSpeed < 0; horizSpeed steers as in moveForward
        void moveBackward(int horizSpeed, int vertSpeed);
        // vel > 0
        void spinRight(int vel);
        // vel < 0 (the stick value): it is negated before use
        void spinLeft(int vel);
        void stopMoving();
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
    ledcWrite(this->m1aChannel, 0);
    ledcWrite(this->m1bChannel, vel);
    ledcWrite(this->m2aChannel, vel);
    ledcWrite(this->m2bChannel, 0);  
}

void WheelsMotorDriver::spinLeft(int vel){
    vel *= -1;
    ledcWrite(this->m1aChannel, vel);
    ledcWrite(this->m1bChannel, 0);
    ledcWrite(this->m2aChannel, 0);
    ledcWrite(this->m2bChannel, vel);
}

void WheelsMotorDriver::stopMoving(){
    ledcWrite(this->m1aChannel, 0);
    ledcWrite(this->m1bChannel, 0);
    ledcWrite(this->m2aChannel, 0);
    ledcWrite(this->m2bChannel, 0);
}


#endif