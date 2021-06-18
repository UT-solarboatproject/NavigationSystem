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
        self.pin_or = pin_or

        self.pins = {
            pin_mode: {
                "name": "mode",
                "done": False,
                "rise_tick": None,
                "pulse_width": 0.0,
            },
            pin_servo: {
                "name": "servo",
                "done": False,
                "rise_tick": None,
                "pulse_width": 0.0,
            },
            pin_thruster: {
                "name": "thruster",
                "done": False,
                "rise_tick": None,
                "pulse_width": 0.0,
            },
            pin_or: {
                "name": "or",
                "done": True,
                "rise_tick": None,
                "pulse_width": 1500.0,
            },
        }
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
        for key, value in self.pins.items():
            if key != self.pin_or:
                value["done"] = False

        def cbf(gpio, level, tick):
            """
            Parameter   Value    Meaning
            GPIO        0-31     The GPIO which has changed state
            level       0-2      0 = change to low (a falling edge)
                                1 = change to high (a rising edge)
                                2 = no level change (a watchdog timeout)
            tick        32 bit   The number of microseconds since boot
                                WARNING: this wraps around from
                                4294967295 to 0 roughly every 72 minutes
            """
            pin_name = self.pins[gpio]["name"]
            done = self.pins[gpio]["done"]
            rise_tick = self.pins[gpio]["rise_tick"]
            # Rising
            if level == 1:
                self.pins[gpio]["rise_tick"] = tick
            # Falling and rise_tick exists
            elif level == 0 and rise_tick is not None:
                pulse = tick - self.pins[gpio]["rise_tick"]
                pulse = pulse
                # print(pulse)
                if 900 < pulse < 2200:
                    self.pins[gpio]["pulse_width"] = pulse
                    self.pins[gpio]["done"] = True

        cb_servo = self.pi.callback(self.pin_servo, pigpio.EITHER_EDGE, cbf)
        cb_thruster = self.pi.callback(self.pin_thruster, pigpio.EITHER_EDGE, cbf)
        cb_mode = self.pi.callback(self.pin_mode, pigpio.EITHER_EDGE, cbf)
        cb_or = self.pi.callback(self.pin_or, pigpio.EITHER_EDGE, cbf)
        while not all([self.pins[o]["done"] for o in self.pins]):
            # print([self.pins[o]["done"] for o in self.pins])
            time.sleep(0.00001)

        # if 700 < self.pins["mode"] < 2300:
        #     self.pins["mode"] = self.pins["mode"]

        # if 1000 < self.pins["servo"] < 2000:
        #     self.pins["servo"] = self.pins["servo"]

        # if 1100 < self.pins["thruster"] < 2000:
        #     if self.pins["thruster"] < 1100:
        #         self.pins["thruster"] = 1100
        #     elif self.pins["thruster"] > 1900:
        #         self.pins["thruster"] = 1900
        #     else:
        #         self.pins["thruster"] = self.pins["thruster"]

        cb_servo.cancel()
        cb_thruster.cancel()
        cb_mode.cancel()
        cb_or.cancel()

        return

    def print_pulse_width(self):
        print("mode:     ", self.pins[self.pin_mode]["pulse_width"], "[us]")
        print("servo:    ", self.pins[self.pin_servo], "[us]")
        print("thruster: ", self.pins[self.pin_thruster], "[us]")
        print("OR_judgement: ", self.pins[self.pin_or], "[us]")
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
