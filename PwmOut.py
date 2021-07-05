#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# PwmOut.py
#
# Solar-boat Project 2019
#   created on: 2019/07/27
#   Author: FENG XUANDA
#

import time

import pigpio

from Params import Params


class PwmOut:
    # [Servo motor]
    # neutral servo pulse width = 1500 microseconds
    # [Brushless motor]
    # neutral thruster pulse width = 1100 microseconds
    # minmum pulse width= 1100 microseconds
    # maximum pulse width= 1900 microseconds

    frequency = 50

    def __init__(self, pin_servo, pin_thruster):
        # GPIO number
        self.pin_servo = pin_servo
        self.pin_thruster = pin_thruster
        self.servo_pulse_width = 1500
        self.thruster_pulse_width = 1100

        # Setup for Out
        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin_servo, pigpio.OUTPUT)
        self.pi.set_mode(self.pin_thruster, pigpio.OUTPUT)
        self.pi.set_servo_pulsewidth(self.pin_servo, 1500)  # neutral
        self.pi.set_servo_pulsewidth(self.pin_thruster, 1100)  # neutral
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
    import sys
    import yaml

    args = sys.argv
    filename = args[1]
    with open(filename, "r") as f:
        params = yaml.safe_load(f)
    try:
        params = Params()
        sample = PwmOut(params.pin_servo_out, params.pin_thruster_out)
        # [Servo motor]
        # neutral servo pulse width = 1500 microseconds
        # [Brushless motor]
        # neutral thruster pulse width = 1100 microseconds
        # minmum pulse width= 1100 microseconds
        # maximum pulse width= 1900 microseconds

        print(
            "Initialize Brushless Motor and Servo Motor. Please reconnect the batteries."
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
        print(
            f"speed = {sample.thruster_pulse_width} direction = {sample.servo_pulse_width}"
        )
        while True:
            sample.update_pulse_width()
            inp = input()
            if inp == "u":
                sample.thruster_pulse_width += 100  # incrementing the speed like hell
                print(
                    f"speed = {sample.thruster_pulse_width} direction = {sample.servo_pulse_width}"
                )
            elif inp == "j":
                sample.thruster_pulse_width -= 100
                print(
                    f"speed = {sample.thruster_pulse_width} direction = {sample.servo_pulse_width}"
                )
            elif inp == "k":
                sample.servo_pulse_width += 100
                print(
                    f"speed = {sample.thruster_pulse_width} direction = {sample.servo_pulse_width}"
                )
            elif inp == "h":
                sample.servo_pulse_width -= 100
                print(
                    f"speed = {sample.thruster_pulse_width} direction = {sample.servo_pulse_width}"
                )
            elif inp == "stop":
                break
            else:
                print("stop or u or j or k or h!")
        print("Execution Succeed.")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        sample.end()
        print("Execution finished.")
