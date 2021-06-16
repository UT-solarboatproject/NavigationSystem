#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# PwmOut.py
#
# Solar-boat Project 2019
#   created on: 2019/07/27
#   Author: FENG XUANDA
#

import pigpio
import time
from Params import Params


class PwmOut:
    # [Servo motor]
    # Stopped     : 1500 microseconds
    # [Brushless motor]
    # Max forward : 1900 microseconds
    # Max reverse : 1100 microseconds

    frequency = 50

    def __init__(self, pin_servo, pin_thruster):
        # GPIO number
        self.pin_servo = pin_servo
        self.pin_thruster = pin_thruster
        self.servo_pulse_width = 1500
        self.thruster_pulse_width = 1500

        # Setup for Out
        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin_servo, pigpio.OUTPUT)
        self.pi.set_mode(self.pin_thruster, pigpio.OUTPUT)
        self.pi.set_servo_pulsewidth(self.pin_servo, 1500)  # neutral
        self.pi.set_servo_pulsewidth(self.pin_thruster, 1500)  # neutral
        return

    def end(self):
        self.pi.set_servo_pulsewidth(self.pin_servo, 1500)  # neutral
        self.pi.set_servo_pulsewidth(self.pin_thruster, 1100)  # neutral
        return

    def update_pulse_width(self):
        self.pi.set_servo_pulsewidth(self.pin_servo, self.servo_pulse_width)
        self.pi.set_servo_pulsewidth(self.pin_thruster, self.thruster_pulse_width)
        return


# test code
if __name__ == "__main__":

    try:
        params = Params()
        sample = PwmOut(params.pin_servo_out, params.pin_thruster_out)
        # servo
        servo_pulse_width = 1500
        # thruster
        minPulse = 1100
        maxPulse = 1900

        print(
            "Initialaze Brushless Motor and Servo Motor. Please reconnect the batteries."
        )
        print("Press Enter after the beeping stops.")
        inp = input()
        if inp == "":
            time.sleep(1)

        print('"Commands are as follows"')
        print('"stop"')
        print('"u" to up speed')
        print('"j" to down speed')
        print('"k" to turn right')
        print('"h" to turn left')
        print("speed = %d" % sample.thruster_pulse_width)
        while True:
            sample.update_pulse_width()
            inp = input()
            if inp == "u":
                sample.thruster_pulse_width += 100  # incrementing the speed like hell
                print(
                    "speed = %d direction = %d"
                    % (sample.thruster_pulse_width, sample.servo_pulse_width)
                )
            elif inp == "j":
                sample.thruster_pulse_width -= 100
                print(
                    "speed = %d direction = %d"
                    % (sample.thruster_pulse_width, sample.servo_pulse_width)
                )
            elif inp == "k":
                sample.servo_pulse_width += 100
                print(
                    "speed = %d direction = %d"
                    % (sample.thruster_pulse_width, sample.servo_pulse_width)
                )
            elif inp == "h":
                sample.servo_pulse_width -= 100
                print(
                    "speed = %d direction = %d"
                    % (sample.thruster_pulse_width, sample.servo_pulse_width)
                )
            elif inp == "stop":
                sample.thruster_pulse_width = 1100
                break
            else:
                print("stop or u or j or k or h!")
        sample.finalize()
        print("Execution Successed.")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        sample.finalize()
        print("Execution finished.")
