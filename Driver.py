#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Driver.py
#
# Solar-boat Project 2019
#   created on: 2019/07/27
#   Author: Tetsuro Ninomiya
#

import math
import sys
import time

import adafruit_ina260
import board
import yaml

from Logger import Logger
from Pid import PositionalPID
from PwmOut import PwmOut
from PwmRead import PwmRead
from Status import Status
from TimeManager import TimeManager


class Driver:
    def __init__(self, filename):
        self.log_time = time.time()
        self._logger = Logger()
        self._logger.open()

        # load config
        print("loading", filename)
        with open(filename, "r") as f:
            params = yaml.safe_load(f)

        # setup time manager
        self._time_manager = TimeManager()
        self._time_manager.set_time_limit(params["time_limit"])  # Time Limit
        self._sleep_time = params["sleep_time"]

        # setup pid
        self._pid = PositionalPID(params["pwm_range"])
        P = params["P"]
        I = params["I"]
        D = params["D"]
        self._pid.set_pid(P, I, D)

        # setup waypoints
        self._status = Status(params["wp_radius"])
        for wp in params["waypoints"]:
            name = wp["name"]
            lat = wp["lat"]
            lon = wp["lon"]
            print(name, lat, lon)
            self._status.waypoint.add_point(lat, lon)

        # setup pwm read/write
        self._pwm_read = PwmRead(
            params["gpio"]["mode"]["in"],
            params["gpio"]["servo"]["in"],
            params["gpio"]["thruster"]["in"],
        )
        self._pwm_out = PwmOut(
            params["gpio"]["servo"]["out"], params["gpio"]["thruster"]["out"]
        )

        self.run_ina = False

        # setup for ina226
        print("Configuring INA226..")
        try:
            i2c = board.I2C()
            self.i_sensor = adafruit_ina260.INA260(i2c, 0x40)
        except:
            print("Error when configuring INA226")

        time.sleep(1)

        print("Configuration Done")

    def check_mode_change(self):
        print(
            "Please set to AN mode and then switch to RC mode to start appropriately."
        )
        self._pwm_read.measure_pulse_width()
        self._update_mode()
        if self._status.mode == "AN":
            print("Next procedure: Set to RC mode to start.")
            while self._status.mode == "AN":
                self._pwm_read.measure_pulse_width()
                self._update_mode()
                time.sleep(0.1)
        elif self._status.mode == "RC":
            print("Next procedure: set to AN mode and then switch to RC mode to start.")
            while self._status.mode == "RC":
                self._pwm_read.measure_pulse_width()
                self._update_mode()
                time.sleep(0.1)
            print("Next procedure: Set to RC mode to start.")
            while self._status.mode == "AN":
                self._pwm_read.measure_pulse_width()
                self._update_mode()
                time.sleep(0.1)
        print("Procedure confirmed.")

    def do_operation(self):
        while self._time_manager.in_time_limit():
            self._pwm_read.measure_pulse_width()
            self._status.read_gps()
            self._update_output()

            if time.time() - self.log_time > 1:
                self.log_time = time.time()
                # for test
                self._pwm_read.print_pulse_width()

                # ina226
                if hasattr(self, "i_sensor"):
                    self.i_sensor.print_status()
                self._print_log()
            time.sleep(self._sleep_time)
        return

    def _update_output(self):
        if self._status.has_finished:
            mode = "RC"
        else:
            self._update_mode()
            mode = self._status.mode
        # RC mode
        if mode == "RC":
            self._rc_operation()
        # AN mode
        elif mode == "AN":
            self._auto_navigation()
        else:
            print("Could not update output based on mode")
        # update pwm output
        self._pwm_out.update_pulse_width()
        return

    def _update_mode(self):
        mode_duty_ratio = self._pwm_read.pins[self._pwm_read.pin_mode]["pulse_width"]
        # RC mode
        if 0 < mode_duty_ratio < 1500:
            self._status.mode = "RC"
        # AN mode
        elif 1500 <= mode_duty_ratio:
            self._status.mode = "AN"
        else:
            print("Error: mode updating failed", file=sys.stderr)
        return

    def _rc_operation(self):
        # Set the readout signals from receiver as the output signals
        self._pwm_out.servo_pulse_width = self._pwm_read.pins[self._pwm_read.pin_servo][
            "pulse_width"
        ]
        self._pwm_out.thruster_pulse_width = self._pwm_read.pins[
            self._pwm_read.pin_thruster
        ]["pulse_width"]
        return

    def _auto_navigation(self):
        # update status
        status = self._status
        status.calc_target_bearing()
        status.calc_target_distance()
        status.update_target()

        target_bearing_relative = math.degrees(self._status.target_bearing_relative)
        target_distance = self._status.target_distance
        servo_pulse_width = self._pid.get_step_signal(
            target_bearing_relative, target_distance
        )
        self._pwm_out.servo_pulse_width = servo_pulse_width
        if self.run_ina:
            self._optimize_thruster()
        else:
            self._pwm_out.thruster_pulse_width = 1900
        return

    def _optimize_thruster(self):
        if self.voltage < 12.15:
            self._pwm_out.thruster_pulse_width -= 150*(12.15 - self.voltage)
        elif self.current < 0.005:
            self._pwm_out.thruster_pulse_width = 1100
        elif self._pwm_out.thruster_pulse_width <= 1900:
            self._pwm_out.thruster_pulse_width += 100
        self._pwm_out.thruster_pulse_width = min(
            max(self._pwm_out.thruster_pulse_width, 1100), 1900
        )

    def _print_log(self):
        timestamp = self._status.timestamp_string
        mode = self._status.mode
        latitude = self._status.latitude
        longitude = self._status.longitude
        speed = self._status.speed
        heading = math.degrees(self._status.boat_heading)
        servo_pw = self._pwm_out.servo_pulse_width
        thruster_pw = self._pwm_out.thruster_pulse_width
        t_bearing = math.degrees(self._status.target_bearing)
        t_bearing_rel = math.degrees(self._status.target_bearing_relative)
        t_distance = self._status.target_distance
        target = self._status.waypoint.get_point()
        t_latitude = target[0]
        t_longitude = target[1]
        t_idx = self._status.waypoint._index
        err = self._pid.err_back
        if hasattr(self, "i_sensor"):
            self.current = self.i_sensor.current
            self.voltage = self.i_sensor.voltage
            self.power = self.i_sensor.power
            self.run_ina = True
        else:
            self.current = 0
            self.voltage = 0
            self.power = 0

        # To print logdata
        print(timestamp)

        print(
            f"Current: {self.current:.3f}A, Voltage: {self.voltage:.3f}V, Power: {self.power:.3f}W"
        )
        print(
            f"[{mode} MODE] LAT={latitude:.7f}, LON={longitude:.7f}, SPEED={speed:.2f} [km/h], HEADING={heading:.2f}"
        )
        print(
            f"DUTY (SERVO, THRUSTER):       ({servo_pw:6.1f}, {thruster_pw:6.1f}) [us]"
        )
        print(f"TARGET INDEX: {t_idx}")
        print(f"TARGET (LATITUDE, LONGITUDE): ({t_latitude:.7f}, {t_longitude:.7f})")
        print(
            f"TARGET (REL_BEARING, DISTANCE): ({t_bearing_rel:5.2f}, {t_distance:5.2f} [m])"
        )
        print("")

        # To write logdata (csv file)
        log_list = [
            timestamp,
            mode,
            latitude,
            longitude,
            heading,
            speed,
            t_idx,
            t_latitude,
            t_longitude,
            t_bearing,
            t_distance,
            servo_pw,
            thruster_pw,
            err,
            self.current,
            self.voltage,
            self.power,
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
