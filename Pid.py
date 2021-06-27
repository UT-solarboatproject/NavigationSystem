#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Pid.py
#
# Solar-boat Project 2019
#   created on: 2019/07/29
#   Author: FENG XUANDA
#
import math


class PositionalPID:
    def __init__(self):
        self.kp = 0.0
        self.ki = 0.0
        self.kd = 0.0

        self.pid_err_sum = 0.0
        self.err_back = 0.0

    def set_pid(self, P, I, D):
        self.kp = P
        self.ki = I
        self.kd = D
        return

    def get_step_signal(self, target_bearing_relative, target_distance):
        err = target_bearing_relative
        # err is within (-180,180), but realistic to assume (-90,90)
        if abs(err) > 90:
            err = math.copysign(90,err)
        kp_term = self.kp * err
        ki_term = self.ki * self.pid_err_sum
        kd_term = self.kd * (err - self.err_back)
        pid_sum = kp_term + ki_term + kd_term

        scale = 33

        temp = math.exp(-pid_sum / scale)
        pid_sum_norm = (2 / (1 + temp)) - 1
        # limit to -1~1
        # y=2/(1+exp(-x/a))-1
        # to get input X for any Y between (-1,1) x = -a*ln((1-Y)/(1+Y))
        # scale was chosen s.t. Y=0.8(80%) when X~72(90*0.8)

        pwm_mid_point = 1500
        pwm_range = 400
        servo_pwm = pwm_mid_point + pwm_range * pid_sum_norm

        self.pid_err_sum += err
        self.err_back = err

        return servo_pwm


if __name__ == "__main__":
    print("pid")
