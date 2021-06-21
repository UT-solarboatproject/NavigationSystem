#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# main.py
#
# Solar-boat Project 2019
#   created on: 2019/07/25
#   Author: Tetsuro Ninomiya
#

import sys
import time


def main():
    # confirm python3
    version_info = sys.version_info
    if version_info.major < 3:
        print("Use python3.")
        print("Usage: python3 main.py [parameter_file]")
        return

    # Command line arguments
    args = sys.argv
    if len(args) < 2:
        print("[ERROR] NO ARGUMENTS")
        print("Usage: python3 main.py [parameter_file]")
        return

    # Initilize
    from Driver import Driver

    driver = Driver()

    try:
        # Load parameters
        driver.load_params(args[1])

        # Confirming initial mode
        print("Please set to AN mode and then switch to RC mode to start appropriately.")
        driver._pwm_read.measure_pulse_width() 
        driver._update_mode()
        if driver._status.mode == "AN":
            print("Next procedure: Set to RC mode to start.")
            while driver._status.mode == "AN":
                driver._pwm_read.measure_pulse_width()
                driver._update_mode()
                time.sleep(0.1)
        elif driver._status.mode == "RC":
            print("Next procedure: set to AN mode and then switch to RC mode to start.")
            while driver._status.mode == "RC":
                driver._pwm_read.measure_pulse_width()
                driver._update_mode()
                time.sleep(0.1)
            while driver._status.mode == "AN":
                driver._pwm_read.measure_pulse_width()
                driver._update_mode()
                time.sleep(0.1)
        print("Procedure confirmed.")
            
        # Control Loop
        driver.do_operation()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        # If you end this program,
        # this program set the system to stop
        driver.end()
        print("finish")


if __name__ == "__main__":
    main()
