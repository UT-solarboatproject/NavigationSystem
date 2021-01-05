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


class State:
    # Constructor
    #   Argument: time_limit[sec]
    # Stopwatch starts when this class is called
    def __init__(self, time_limit):
        self.time_limit = time_limit
        self.start_stop_watch()

    def start_stop_watch(self):
        self.start_time = time.time()

    def get_elapsed_time(self):
        elapsed_time = time.time() - self.start_time
        return elapsed_time

    # This function returns:
    #   Within the time limit -> True
    #   Not -> False
    def in_time_limit(self):
        elapsed_time = self.get_elapsed_time()
        return elapsed_time < self.time_limit


if __name__ == "__main__":
    state = State(10)
    time.sleep(5)
    print(state.in_time_limit())
    time.sleep(5)
    print(state.in_time_limit())
