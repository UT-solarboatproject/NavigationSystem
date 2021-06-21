#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# GpsData.py
#
# Solar-boat Project 2019
#   created on: 2019/07/29
#   Author: Xu Guanglei
#

import copy
import threading
import time

from micropyGPS import MicropyGPS
from serial import Serial


class GpsData:
    def __init__(self):
        self.timestamp = [0, 0, 0.0]
        self.timestamp_string = ""
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.speed = []
        self.course = 0.0
        self.satellites_used = []
        self.satellite_data = {}
        try:
            self.serial = Serial("/dev/serial0", 9600, timeout=10)
        except:
            self.serial = Serial("/dev/ttyACM0", 9600, timeout=10)
            print("Exception occured. Switching to a different serial port.")
        self.gps = MicropyGPS(9, "dd")
        self.gpsthread = threading.Thread(target=self.run_gps, args=())
        self.gpsthread.daemon = True
        self.gpsthread.start()

    def run_gps(self):
        s = self.serial
        s.reset_input_buffer()
        s.readline()
        while True:
            try:
                sentence = s.readline().decode("utf-8")
            except UnicodeDecodeError:
                s.reset_input_buffer()
                continue
            try:
                if sentence[0] != "$":
                    continue
            except IndexError as e:
                print(
                    "No data incoming. Check raspi-config and disable Linux serial console: https://www.raspberrypi.org/documentation/configuration/uart.md#:~:text=Disable%20Linux%20serial%20console&text=This%20can%20be%20done%20by,Select%20option%20P6%20%2D%20Serial%20Port."
                )
                raise e
            else:
                for x in sentence:
                    self.gps.update(x)

    def read(self):
        if self.gps.parsed_sentences > 0:
            h = (
                self.gps.timestamp[0]
                if self.gps.timestamp[0] < 24
                else self.gps.timestamp[0] - 24
            )
            self.timestamp[0] = h
            self.timestamp[1] = self.gps.timestamp[1]
            self.timestamp[2] = self.gps.timestamp[2]
            t = self.timestamp
            self.timestamp_string = "%2d:%02d:%04.1f" % (t[0], t[1], t[2])
            self.latitude = self.gps.latitude[0]
            self.longitude = self.gps.longitude[0]
            self.altitude = self.gps.altitude
            self.course = self.gps.course
            self.speed = copy.deepcopy(self.gps.speed)
            self.satellites_used = copy.deepcopy(self.gps.satellites_used)
            self.satellite_data = copy.deepcopy(self.gps.satellite_data)
            return True
        else:
            return False

    def print(self):
        t = self.timestamp
        lat = self.latitude
        lon = self.longitude
        alt = self.altitude
        print("%2d:%02d:%04.1f" % (t[0], t[1], t[2]))
        print("latitude: %.5f, longitude: %.5f" % (lat, lon))
        print("altitude: %f" % (alt))
        print("course: %f" % (self.course))
        print("speed:", self.speed)
        print("Satellites Used: ", self.satellites_used)
        for k, v in self.satellite_data.items():
            print("%d: %s" % (k, v))
        print("")
        return


if __name__ == "__main__":
    gps_data = GpsData()
    while True:
        time.sleep(3.0)
        if gps_data.read():
            gps_data.print()
