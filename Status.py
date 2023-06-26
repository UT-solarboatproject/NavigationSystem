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
import sys

from GpsData import GpsData
from Waypoint import Waypoint


class Status:
    def __init__(self, radius, waypointIndex):
        self.waypoint = Waypoint(waypointIndex)
        self.mode = "TEST"
        self.speed = 0.0
        self.boat_heading = 0.0
        self.latitude = 0.0
        self.longitude = 0.0
        self.previous_recorded_latitude = 0.0
        self.previous_recorded_longitude = 0.0
        self.timestamp_string = ""
        self.target_bearing = 0.0
        self.target_bearing_relative = 0.0
        self.target_distance = 0.0
        self.wp_radius = radius
        self.gps_data = GpsData()
        self.has_finished = False

    def read_gps(self):
        if self.gps_data.read():
            lat1, lon1 = self.latitude, self.longitude
            lat2, lon2 = (
                self.previous_recorded_latitude,
                self.previous_recorded_longitude,
            )
            distance = self._get_distance(lat1, lon1, lat2, lon2)
            if distance >= 2:  # meter
                self.boat_heading = self._get_heading(
                    self.previous_recorded_latitude,
                    self.previous_recorded_longitude,
                    self.latitude,
                    self.longitude,
                )
                self.previous_recorded_latitude = self.gps_data.latitude
                self.previous_recorded_longitude = self.gps_data.longitude
            self.timestamp_string = self.gps_data.timestamp_string
            self.latitude = self.gps_data.latitude
            self.longitude = self.gps_data.longitude
            self.speed = self.gps_data.speed[2]  # kph
            return True
        else:
            return False

    def calc_target_distance(self):
        """
        Calculate the distance between the current location and the current waypoint in meters
        """
        wp_coordinate = self.waypoint.get_point()
        lat1, lon1 = self.latitude, self.longitude
        lat2, lon2 = wp_coordinate[0], wp_coordinate[1]
        self.target_distance = self._get_distance(lat1, lon1, lat2, lon2)
        return

    def calc_target_bearing(self):
        """
        Calculate the current waypoint's bearing and relative bearing (relative to boat heading) in radians
        """
        wp_coordinate = self.waypoint.get_point()
        lat1, lon1 = self.latitude, self.longitude
        lat2, lon2 = wp_coordinate[0], wp_coordinate[1]
        self.target_bearing = self._get_heading(lat1, lon1, lat2, lon2)
        self.target_bearing_relative = self.target_bearing - self.boat_heading
        return

    @staticmethod
    def _get_heading(lat1, lon1, lat2, lon2):
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

    @staticmethod
    def _get_distance(lat1, lon1, lat2, lon2):
        """
        Returns distance between (lon1, lat1) & (lon2, lat2) in meters
        """
        r = 6378.137  # [km] # radius of the Earth
        theta1, phi1 = map(math.radians, [lat1, lon1])
        theta2, phi2 = map(math.radians, [lat2, lon2])
        dphi = phi2 - phi1
        dtheta = theta2 - theta1
        a = (
            math.sin(dtheta / 2) ** 2
            + math.cos(theta1) * math.cos(theta2) * math.sin(dphi / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        distance = c * r * 1000  # [m]
        return distance

    def _has_passed_way_point(self):
        return self.target_distance < self.wp_radius

    def update_target(self):
        if self._has_passed_way_point():
            # If the boat has passed all waypoints, key is false
            # If not, key is true
            key = self.waypoint.next_point()
            if not key:
                print("AN has finished!")
                self.has_finished = True
        return


if __name__ == "__main__":
    # Command line arguments
    args = sys.argv

    status = Status(args[1] if args[1] else 10, args[2] if args[2] else 0)