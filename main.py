#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# main.py
#
# Solar-boat Project 2019
#   created on: 2019/07/25
#   Author: Tetsuro Ninomiya
#

import argparse
import sys


def main():
    # confirm python3
    version_info = sys.version_info
    if version_info.major < 3:
        print("Use python3.")
        print("Usage: python3 main.py [parameter_file]")
        return

    # Command line arguments
    args = _parse_args()

    # Initialize
    from Driver import Driver

    driver = Driver()

    try:
        # Load parameters
        driver.load_params(args.input_file_path, args.write_waypoints_fig)

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


def _parse_args():
    """
    input_file_path: input fileのpath
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file_path")
    parser.add_argument("-ww", "--write_waypoints_fig", action="store_true")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
