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

import pigpio


class PwmRead:
    def __init__(self, pin_mode, pin_servo, pin_thruster, pin_or):
        self.pin_servo = pin_servo
        self.pin_thruster = pin_thruster
        self.pin_mode = pin_mode
        self.pin_or = pin_or

        self.pins = {
            pin_mode: {
                "done_reading": False,
                "rise_tick": None,
                "pulse_width": 0.0,
            },
            pin_servo: {
                "done_reading": False,
                "rise_tick": None,
                "pulse_width": 0.0,
            },
            pin_thruster: {
                "done_reading": False,
                "rise_tick": None,
                "pulse_width": 0.0,
            },
            pin_or: {
                "done_reading": True,
                "rise_tick": None,
                "pulse_width": 1500.0,
            },
        }

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
            if (
                key != self.pin_or
            ):  # Temporary measure to disable OR mode (may be deprecated in the future)
                value["done_reading"] = False
            value["rise_tick"] = None

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
            rise_tick = self.pins[gpio]["rise_tick"]
            # Rising
            if level == 1:
                self.pins[gpio]["rise_tick"] = tick
            # Falling and rise_tick exists
            elif level == 0 and rise_tick is not None:
                pulse = tick - self.pins[gpio]["rise_tick"]
                if 900 < pulse < 2200:
                    self.pins[gpio]["pulse_width"] = pulse
                    self.pins[gpio]["done_reading"] = True

        read_edge = pigpio.EITHER_EDGE
        cb_servo = self.pi.callback(self.pin_servo, read_edge, cbf)
        cb_thruster = self.pi.callback(self.pin_thruster, read_edge, cbf)
        cb_mode = self.pi.callback(self.pin_mode, read_edge, cbf)
        cb_or = self.pi.callback(self.pin_or, read_edge, cbf)
        while not all([self.pins[gpio]["done_reading"] for gpio in self.pins]):
            time.sleep(0.00001)

        cb_servo.cancel()
        cb_thruster.cancel()
        cb_mode.cancel()
        cb_or.cancel()

    def print_pulse_width(self):
        print("mode:     ", self.pins[self.pin_mode]["pulse_width"], "[us]")
        print("servo:    ", self.pins[self.pin_servo]["pulse_width"], "[us]")
        print("thruster: ", self.pins[self.pin_thruster]["pulse_width"], "[us]")
        print("OR_judgement: ", self.pins[self.pin_or]["pulse_width"], "[us]")
        print("")

    def end(self):
        self.pi.stop()


# test code
if __name__ == "__main__":
    from Params import Params

    try:
        print("Attempting to recieve signal....")
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

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        pwm_read.end()
        print("Execution finished.")
