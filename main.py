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

    # Initialize
    from Driver import Driver

    driver = Driver(args[1], int(args[2]) if len(args)==3 else 0)

    try:
        # Confirming initial mode
        driver.check_mode_change()

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
