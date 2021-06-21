#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Status.py
#
# Solar-boat Project 2019
#   created on: 2019/07/27
#   Author: Tetsuro Ninomiya
#

import math

from GpsData import GpsData
from Params import Params
from Waypoint import Waypoint
from geopy.distance import geodesic


class Status:
    def __init__(self, params):
        self.params = params
        self.waypoint = Waypoint()
        self.mode = "TEST"
        self.speed = 0.0
        self.boat_heading = 0.0
        self.latitude = 0.0
        self.longitude = 0.0
        self.timestamp_string = ""
        self.target_bearing = 0.0
        self.target_bearing_relative = 0.0
        self.target_distance = 0.0
        self.gps_data = GpsData()
        self.gps_data_for_out_of_range = None

    def read_gps(self):
        if self.gps_data.read():
            current_location = (self.gps_data.latitude, self.gps_data.longitude)
            prev_location = (self.latitude, self.longitude)
            distance = geodesic(current_location, prev_location).km
            if distance >= 0.002:  # km
                self.boat_heading = self._get_heading(
                    self.longitude,
                    self.latitude,
                    self.gps_data.longitude,
                    self.gps_data.latitude,
                )
            self.timestamp_string = self.gps_data.timestamp_string
            if not self.gps_data_for_out_of_range:
                self.gps_data_for_out_of_range = {
                    "latitude": self.gps_data.latitude,
                    "longitude": self.gps_data.longitude,
                }
            self.latitude = self.gps_data.latitude
            self.longitude = self.gps_data.longitude
            self.speed = self.gps_data.speed[2]  # kph
            return True
        else:
            return False

    def calc_target_distance(self):
        r = 6378.137  # [km] # radius of the Earth
        wp = self.waypoint
        theta1, phi1 = map(math.radians, [self.latitude, self.longitude])
        theta2, phi2 = map(math.radians, wp.get_point())
        dphi = phi2 - phi1
        dtheta = theta2 - theta1
        a = (
            math.sin(dtheta / 2) ** 2
            + math.cos(theta1) * math.cos(theta2) * math.sin(dphi / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        self.target_distance = c * r * 1000  # [m]
        return

    def calc_target_bearing(self):
        """
        Calculate the current waypoint's bearing and relative bearing (relative to boat heading) in radians
        """
        wp = self.waypoint
        theta1, phi1 = map(math.radians, [self.latitude, self.longitude])
        theta2, phi2 = map(math.radians, wp.get_point())
        dphi = phi2 - phi1
        y = math.sin(dphi) * math.cos(theta2)
        x = math.cos(theta1) * math.sin(theta2)
        -math.sin(theta1) * math.cos(theta2) * math.cos(dphi)
        bearing = math.atan2(y, x)
        self.target_bearing = bearing  # rad
        self.target_bearing_relative = bearing - self.boat_heading
        return

    @staticmethod
    def _get_heading(lon1, lat1, lon2, lat2):
        """
        Returns boat heading(relative to north pole) in radians
        """
        theta1, phi1 = map(math.radians, [lat1, lon1])
        theta2, phi2 = map(math.radians, [lat2, lon2])
        dphi = phi2 - phi1
        y = math.sin(dphi) * math.cos(theta2)
        x = math.cos(theta1) * math.sin(theta2) - math.sin(theta1) * math.cos(
            theta2
        ) * math.cos(dphi)
        dir = math.atan2(y, x)
        return dir

    def _has_passed_way_point(self):
        return self.target_distance < 90.0

    def update_target(self):
        if self._has_passed_way_point():
            # If the boat has passed all waypoints, key is false
            # If not, key is true
            key = self.waypoint.next_point()
            if not key:
                print("AN has finished!")
                self.mode = "RC"
        return

    def update_way_point(self):
        try:
            self.waypoint = Waypoint(
                [self.gps_data_for_out_of_range["latitude"]],
                [self.gps_data_for_out_of_range["longitude"]],
            )
        except TypeError:
            print("Error: No gps_data_history but now out of range!")


if __name__ == "__main__":
    params = Params()
    status = Status(params)
