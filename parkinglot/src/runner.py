#!/usr/bin/python
import os, sys

from src.parking import Lot


class Runner(object):
    def __init__(self):
        self.lot = Lot()

    # region input processors
    def process_input(self):
        try:
            while True:
                stdin_input = input("Enter command: ")
                self.process_command(stdin_input)
        except (KeyboardInterrupt, SystemExit):
            return
        except Exception as ex:
            print("Error occured while processing input %s" % ex)

    def process_command(self, stdin_input):
        inputs = stdin_input.split()
        command = inputs[0]
        params = inputs[1:]
        if hasattr(self.lot, command):
            command_function = getattr(self.lot, command)
            command_function(*params)
        else:
            print("Got wrong command.")
    # endregion


# region Main entry point
if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        runner = Runner()
        runner.process_input()
    elif len(args) == 2:
        runner = Runner()
        runner.process_file(args[1])
    else:
        print("Wrong number of arguments.\n"
              "Usage:\n"
              "./parking_lot.py <filename> OR \n"
              "./parking_lot.py")
# endregion
