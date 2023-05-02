#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# State.py
#
# Solar-boat Project 2019
#   created on: 2019/07/25
#   Author: Tetsuro Ninomiya
#

import time


class TimeManager:
    # Constructor
    #   Argument: time_limit[sec]
    # Stopwatch starts when this class is called
    def __init__(self, time_limit=10**12):
        self._time_limit = time_limit
        self._start_time = time.time()

    def set_time_limit(self, sec: int):
        self._time_limit = sec

    def get_elapsed_time(self):
        elapsed_time = time.time() - self._start_time
        return elapsed_time

    # This function returns:
    #   Within the time limit -> True
    #   Not -> False
    def in_time_limit(self):
        elapsed_time = self.get_elapsed_time()
        return elapsed_time < self._time_limit


if __name__ == "__main__":
    state = TimeManager(10)
    time.sleep(5)
    print(state.in_time_limit())
    time.sleep(5)
    print(state.in_time_limit())
