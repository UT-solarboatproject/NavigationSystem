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


def main():
    # confirm python3
    version_info = sys.version_info
    try:
        assert version_info.major >= 3
    except AssertionError:
        print("Use python3.")
        print("Usage: python3 main.py [parameter_file]")
        return

    # Initilize
    from Driver import Driver

    driver = Driver()

    try:
        # Command line arguments
        args = sys.argv
        if len(args) < 2:
            raise InitialArgumentsError
        # Load parameters
        driver.load(args[1])
        # Control Loop
        driver.do_operation()
    except InitialArgumentsError:
        print("[ERROR] NO ARGUMENTS")
        print("Usage: python3 main.py [parameter_file]")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        # If you finalize this program,
        # this program set the system to stop
        driver.finalize()
        print("finish")


class InitialArgumentsError(Exception):
    pass


if __name__ == "__main__":
    main()
