#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Pwm.py
#
# Solar-boat Project 2019
#   created on: 2019/08/01
#   Author: Tetsuro Ninomiya
#

import time
from queue import Queue
from time import sleep

import pigpio


class PwmRead:
    def __init__(self, pin_mode, pin_servo, pin_thruster, pin_or):
        self.pin_servo = pin_servo
        self.pin_thruster = pin_thruster
        self.pin_mode = pin_mode
        self.pulse_width = {
            "mode": 0.0,
            "servo": 0.0,
            "thruster": 0.0,
            "OR": 1500.0,
        }  # [us] # mode, servo, thruster, OR
        self.pin_or = pin_or
        self.pin_name_dict = {pin_mode: "mode", pin_servo: "servo",
                              pin_thruster: "thruster", pin_or: "OR"}
        # variables for out of range
        self._or_queue = Queue()
        self._or_queue_size = 20
        for _ in range(self._or_queue_size):
            self._or_queue.put(1500)
        self._or_mean = 1500

        # setup for pigpio

        self.pi = pigpio.pi()
        self.pi.set_mode(pin_servo, pigpio.INPUT)
        self.pi.set_mode(pin_thruster, pigpio.INPUT)
        self.pi.set_mode(pin_mode, pigpio.INPUT)
        self.pi.set_mode(pin_or, pigpio.INPUT)

    def measure_pulse_width(self):
        """
        PWM frequency is 50 Hz
        So a pulse width must be under 20 ms
        The range of the receiver's signal(ON) is 1.0 ~ 2.0 ms
        1.0 ms : LOW
        1.5 ms : Neutral
        2.0 ms : HIGH

        There is a little delay, 0.01 ~ 0.03 ms
        For an error, if range is above 2.0 ms, not counted

        (M-02)
        [MODE]
        above 2.0 ms : DOWN
        under 1.0 ms : UP

        [SERVO][THRUSTER]
        max 1.94 ms     : DOWN
        neutral 1.53 ms
        min 1.13 ms     : UP
        """
        def callback(pin):
            pin_name = self.pin_name_dict[pin]

            def cbf(gpio, level, tick):
                if level == 1:
                    self.up[pin_name] = tick
                elif level == 0 and self.up[pin_name] is not None:
                    pulse = self.up[pin_name] - tick
                    pulse = pulse * 10 ** 6
                    if 900 < pulse < 2200:
                        self.pulse_width[pin_name] = pulse
                        self.done[pin_name] = True
            return cbf

        self.pi.callback(self.pin_servo, pigpio.EITHER_EDGE,
                         callback(self.pin_servo))
        self.pi.callback(self.pin_thruster, pigpio.EITHER_EDGE,
                         callback(self.pin_thruster))
        self.pi.callback(self.pin_mode, pigpio.EITHER_EDGE,
                         callback(self.pin_mode))
        self.pi.callback(self.pin_or, pigpio.EITHER_EDGE,
                         callback(self.pin_or))
        while not all(self.done):
            sleep(0.0001)

        if 700 < self.pulse_width["mode"] < 2300:
            self.pulse_width["mode"] = self.pulse_width["mode"]

        if 1000 < self.pulse_width["servo"] < 2000:
            self.pulse_width["servo"] = self.pulse_width["servo"]

        if 1000 < self.pulse_width["thruster"] < 2000:
            if self.pulse_width["thruster"] < 1100:
                self.pulse_width["thruster"] = 1100
            elif self.pulse_width["thruster"] > 1900:
                self.pulse_width["thruster"] = 1900
            else:
                self.pulse_width["thruster"] = self.pulse_width["thruster"]

        return

    def print_pulse_width(self):
        print("mode:     ", self.pulse_width["mode"], "[us]")
        print("servo:    ", self.pulse_width["servo"], "[us]")
        print("thruster: ", self.pulse_width["thruster"], "[us]")
        print("OR_judgement: ", self.pulse_width["OR"], "[us]")
        print("")
        return

    def end(self):
        self.pi.stop()
        return


# test code
if __name__ == "__main__":
    from Params import Params

    params = Params()
    pwm_read = PwmRead(
        params.pin_mode_in,
        params.pin_servo_in,
        params.pin_thruster_in,
        params.pin_or,
    )
    for i in range(20):
        time.sleep(1)
        pwm_read.measure_pulse_width()
        pwm_read.print_pulse_width()
    pwm_read.end()
