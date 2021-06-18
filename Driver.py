#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Driver.py
#
# Solar-boat Project 2019
#   created on: 2019/07/27
#   Author: Tetsuro Ninomiya
#

import json
import sys
import time

from ina226 import ina226
from Logger import Logger
from Params import Params
from Pid import PositionalPID
from PwmOut import PwmOut
from PwmRead import PwmRead
from Status import Status
from TimeManager import TimeManager

INA226_ADDRESS = 0x40

ina226_averages_t = dict(
    INA226_AVERAGES_1=0b000,
    INA226_AVERAGES_4=0b001,
    INA226_AVERAGES_16=0b010,
    INA226_AVERAGES_64=0b011,
    INA226_AVERAGES_128=0b100,
    INA226_AVERAGES_256=0b101,
    INA226_AVERAGES_512=0b110,
    INA226_AVERAGES_1024=0b111,
)


class Driver:
    def __init__(self):
        self._time_manager = TimeManager()
        self._params = Params()
        self._status = Status(self._params)
        self._sleep_time = 1
        self.log_time = time.time()
        self._pwm_read = PwmRead(
            self._params.pin_mode_in,
            self._params.pin_servo_in,
            self._params.pin_thruster_in,
            self._params.pin_or,
        )
        self._pwm_out = PwmOut(
            self._params.pin_servo_out, self._params.pin_thruster_out
        )
        self._pid = PositionalPID()
        self._logger = Logger()
        self._logger.open()
        # Whether experienced OR mode or not
        self._or_experienced = False

        # setup for ina226
        print("Configuring INA226..")
        try:
            self.i_sensor = ina226(INA226_ADDRESS, 1)
            self.i_sensor.configure(
                avg=ina226_averages_t["INA226_AVERAGES_4"],
            )
            self.i_sensor.calibrate(rShuntValue=0.002, iMaxExcepted=1)
            self.i_sensor.log()
            print("Mode is " + str(hex(self.i_sensor.getMode())))
        except:
            print("Error when configuring INA226")

        time.sleep(1)

        print("Configuration Done")

    def load_params(self, filename):
        print("loading", filename)
        with open(filename, "r") as f:
            params = json.load(f)

        time_limit = params["time_limit"]
        sleep_time = params["sleep_time"]
        P = params["P"]
        I = params["I"]
        D = params["D"]

        self._time_manager.set_time_limit(time_limit)  # Time Limit
        self._sleep_time = float(sleep_time)  # Sleep time
        self._pid.set_pid(P, I, D)

        for wp in params["waypoints"]:
            name = wp["name"]
            lat = wp["lat"]
            lon = wp["lon"]
            print(name, lat, lon)
            self._status.waypoint.add_point(lat, lon)
        return

    def do_operation(self):
        while self._time_manager.in_time_limit():
            # update pwm
            # Read pwm pulse width
            self._pwm_read.measure_pulse_width()
            # Set the readout signals as the output signals
            self._pwm_out.servo_pulse_width = self._pwm_read.pins[
                self._pwm_read.pin_servo
            ]["pulse_width"]
            self._pwm_out.thruster_pulse_width = self._pwm_read.pins[
                self._pwm_read.pin_thruster
            ]["pulse_width"]

            # read gps
            self._status.read_gps()

            self._update_mode()

            # for test
            self._pwm_read.print_pulse_width()

            
            mode = self._status.mode
            if mode == "RC":
                pass
            elif mode == "AN":
                self._auto_navigation()
            elif mode == "OR":
                self._out_of_range_operation()

            # update output
            self._pwm_out.update_pulse_width()

            if time.time() - self.log_time > 1:
                self.log_time = time.time()
                # for test
                self._pwm_read.print_pulse_width()

                # ina226
                if hasattr(self, "i_sensor"):
                    self.i_sensor.log()
                self._print_log()
                # time.sleep(self._sleep_time)
        return

    def _update_mode(self):
        # mode_duty_ratio = self._pwm_read.pulse_width["mode"]
        # or_pulse = self._pwm_read.pulse_width["OR"]
        # # OR mode
        # if or_pulse < 1300 or (1500 <= mode_duty_ratio and self._or_experienced):
        #     if not self._or_experienced:
        #         self._status.update_way_point()
        #     self._status.mode = "OR"
        #     self._or_experienced = True
        # # RC mode
        # elif 0 < mode_duty_ratio < 1500:
        #     self._status.mode = "RC"
        # # AN mode
        # elif 1500 <= mode_duty_ratio and not self._or_experienced:
        #     self._status.mode = "AN"
        # else:
        #     print("Error: mode updating failed", file=sys.stderr)
        self._status.mode = "RC"
        return

    def _auto_navigation(self):
        # update status
        status = self._status
        status.calc_target_direction()
        status.calc_target_distance()
        status.update_target()

        boat_direction = self._status.boat_direction
        target_direction = self._status.target_direction
        servo_pulse_width = self._pid.get_step_signal(target_direction, boat_direction)
        self._pwm_out.servo_pulse_width = servo_pulse_width
        self._pwm_out.thruster_pulse_width = 1700
        return

    def _out_of_range_operation(self):
        # Be stationary
        # self.pwm_out.end()
        # update waypoint where the boat was
        self._auto_navigation()
        return

    def _print_log(self):
        timestamp = self._status.timestamp_string
        mode = self._status.mode
        latitude = self._status.latitude
        longitude = self._status.longitude
        speed = self._status.speed
        direction = self._status.boat_direction
        servo_pw = self._pwm_out.servo_pulse_width
        thruster_pw = self._pwm_out.thruster_pulse_width
        t_direction = self._status.target_direction
        t_distance = self._status.target_distance
        target = self._status.waypoint.get_point()
        t_latitude = target[0]
        t_longitude = target[1]
        err = self._pid.err_back
        if hasattr(self, "i_sensor"):
            current = str(round(self.i_sensor.readShuntCurrent(), 3))
            voltage = str(round(self.i_sensor.readBusVoltage(), 3))
            power = str(round(self.i_sensor.readBusPower(), 3))
        else:
            current = 0
            voltage = 0
            power = 0

        # To print logdata
        print(timestamp)
        print(
            "[%s MODE] LAT=%.7f, LON=%.7f, SPEED=%.2f [km/h], DIRECTION=%lf"
            % (mode, latitude, longitude, speed, direction)
        )
        print(
            "DUTY (SERVO, THRUSTER):       (%6.1f, %6.1f) [us]"
            % (servo_pw, thruster_pw)
        )
        print("TARGET (LATITUDE, LONGITUDE): (%.7f, %.7f)" % (t_latitude, t_longitude))
        print(
            "TARGET (DIRECTION, DISTANCE): (%5.2f, %5.2f [m])"
            % (t_direction, t_distance)
        )
        print("")

        # To write logdata (csv file)
        log_list = [
            timestamp,
            mode,
            latitude,
            longitude,
            direction,
            speed,
            t_latitude,
            t_longitude,
            servo_pw,
            thruster_pw,
            t_direction,
            t_distance,
            err,
            current,
            voltage,
            power,
        ]
        self._logger.write(log_list)
        return

    def end(self):
        self._logger.close()
        self._pwm_read.end()
        self._pwm_out.end()
        return


if __name__ == "__main__":
    print("Driver")
    driver = Driver()
    driver.load("parameter_sample.txt")
