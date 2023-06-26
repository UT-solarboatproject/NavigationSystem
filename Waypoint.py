#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Waypoint.py
#
# Solar-boat Project 2019
#   created on: 2019/07/27
#   Author: Tetsuro Ninomiya
#
import sys

class Waypoint:
    def __init__(self, waypointIndex, latitude=None, longitude=None):
        if longitude is None:
            longitude = []
        if latitude is None:
            latitude = []
        self.latitude = latitude
        self.longitude = longitude
        self._index = waypointIndex
        print("initial waypoint index: ", self._index)
        self._num = 0

    def add_point(self, latitude, longitude):
        self.latitude.append(latitude)
        self.longitude.append(longitude)
        self._num += 1
        return

    def get_point(self):
        latitude = self.latitude[self._index]
        longitude = self.longitude[self._index]
        return [latitude, longitude]

    def next_point(self):
        self._index += 1
        if self._index == self._num:
            return False
        else:
            return True


if __name__ == "__main__":
    # Command line arguments
    args = sys.argv
    waypoint = Waypoint(args[1] if args[1] else 0)

    print("waypoint")
