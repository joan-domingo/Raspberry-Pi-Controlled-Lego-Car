#!/usr/bin/python3

import time
import brickpi3
import pygame

BP = brickpi3.BrickPi3()

# call this function to turn off the motors and exit safely.
def SafeExit():
    # Unconfigure the sensors, disable the motors
    # and restore the LED to the control of the BrickPi3 firmware.
    BP.reset_all()

#Power motor A and B, forward or backward
def powerMotors(power):            
    try:
        if power > 100:
            power = 100
        elif power < -100:
            power = -100
    except IOError as error:
        print(error)
        power = 0

    #print('power', power)
    BP.set_motor_power(BP.PORT_A + BP.PORT_B, power)
        
    # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.
    time.sleep(0.02)

#Steering motor C, turn left or right
def steeringMotor(position):
    try:
        target = BP.get_motor_encoder(BP.PORT_C) # read motor C's position
    except IOError as error:
        print(error)

    #print("turn to ", position)
    BP.set_motor_position(BP.PORT_C, position)
        
    # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.
    time.sleep(0.02)
    

def isMovingLeft(value, events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                return 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                return 0
    return value

def isMovingRight(value, events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                return 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                return 0
    return value

def isMovingBackward(value, events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                return 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                return 0
    return value

def isMovingForward(value, events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                return 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                return 0
    return value

def isImmediateStop(events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                return 0
    return 0

def initBrickPi():
    # make sure voltage is high enough
    if BP.get_voltage_battery() < 7:
        print("Battery voltage below 7v, too low to run motors reliably. Exiting.")
        SafeExit()
        
    try:
        BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A))
        BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_B))
        BP.offset_motor_encoder(BP.PORT_C, BP.get_motor_encoder(BP.PORT_C))
    except IOError as error:
        print(error)

    BP.set_motor_power(BP.PORT_C, BP.MOTOR_FLOAT)
    BP.set_motor_position(BP.PORT_C, 0)

def initPygame():
    pygame.init()
    screen = pygame.display.set_mode((200, 100))
    clock = pygame.time.Clock()


def main():
    try:
        initBrickPi()
        initPygame()

        forward = 0
        backward = 0
        right = 0
        left = 0
        
        speed = 0
        turn = 0
            
        while True:

            events = pygame.event.get()
            forward = isMovingForward(forward, events)
            backward = isMovingBackward(backward, events)
            right = isMovingRight(right, events)
            left = isMovingLeft(left, events)
            immediateStop = isImmediateStop(events)

            if forward:
                if speed > -100:
                    speed = speed - 1
                else:
                    speed = -100
            elif backward:
                if speed < 100:
                    speed = speed + 1
                else:
                    speed = 100
            else:
                if speed > 0:
                    speed = speed - 1
                elif speed < 0:
                    speed = speed + 1
                else:
                    speed = 0

            if immediateStop:
                powerMotors(0)
            else:
                powerMotors(speed)

            if right:
                if turn < 100:
                    turn = turn +10
                else:
                    turn = 100
            elif left:
                if turn > -100:
                    turn = turn -10
                else:
                    turn = -100
            else:
                if turn > 0:
                    turn = turn -10
                elif turn < 0:
                    turn = turn +10
                else:
                    turn = 0

            steeringMotor(turn)

    except KeyboardInterrupt:
        SafeExit()

main()
