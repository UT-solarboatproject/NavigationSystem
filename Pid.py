#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Pid.py
#
# Solar-boat Project 2019
#   created on: 2019/07/29
#   Author: FENG XUANDA
#


class PositionalPID:
    def __init__(self):
        self.kp = 0.0
        self.ki = 0.0
        self.kd = 0.0

        self.result_value_back = 0.0
        self.pid_output = 0.0
        self.pid_err_add = 0.0
        self.err_back = 0.0

    def set_pid(self, P, I, D):
        self.kp = P
        self.ki = I
        self.kd = D
        return

    def get_step_signal(self, target_angle, system_output):

        import math

        err = target_angle - system_output
        # print("PID Err: ",Err)
        kp_work = self.kp * err
        ki_work = self.ki * self.pid_err_add
        kd_work = self.kd * (err - self.err_back)
        self.pid_output = kp_work + ki_work + kd_work
        temp = math.exp(-self.pid_output)

        self.pid_output = (1 / (1 + temp)) - 0.5

        direction = self.pid_output * 150

        duty = 1000 / 180 * (direction + 90) + 1000

        self.pid_err_add += err
        self.err_back = err

        return duty


if __name__ == "__main__":
    print("pid")
