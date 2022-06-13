"""
General Use logger for keeping track of what goes on during an observation night.
"""


import time
from datetime import datetime
import os


class Logger:
    def __init__(self, save_path=None):
        if self.save_path is not None:
            self.save_path = save_path
        else:
            self.save_path = "~/Nightlylogs"
        self.skip = False

    def set_file(self, fname):
        if fname == None:
            self.skip = True
            return
        else:
            if not fname.endswith(".log"):
                self.skip = False
                self.fname = fname + ".log"
            elif fname.endswith(".log"):
                self.fname = fname
            with open(self.fname, "w") as f:
                f.write("Logfile Created at {} \n".format(datetime.now()))

    def setup_db(self, name=None):
        if name is None:
            name = datetime.now().strftime("%Y-%m-%d.asdf")
            self.db = self.save_path + name

    def write_db(self, webrequest_summary):
        time_write = datetime.now().strftime("%Y-%M-%D %HH:%MM:%SS")
        df_units = list(webrequest_summary.df.index.values)  # used in command
        tree = {
            "time": time_write,
        }

    def info(self, s):
        if self.skip:
            return
        with open(self.fname, "a") as f:
            now = str(datetime.datetime.now())
            f.write("{} : INFO : {} \n".format(now, s))

    def warning(self, s):
        if self.skip:
            return
        with open(self.fname, "a") as f:
            now = str(datetime.datetime.now())
            f.write("{} : WARNING : {} \n".format(now, s))

    def vspace(self, n):
        if self.skip:
            return
        with open(self.fname, "a") as f:
            string = "\n" * n
            f.write(string)

    def section(self, s):
        if self.skip:
            return
        with open(self.fname, "a") as f:
            string = "\n \n {} \n -------------------------------------- \n".format(s)
            f.write(string)
