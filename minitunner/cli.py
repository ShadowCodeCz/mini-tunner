import os
import datetime
import logging
import platform
import socket
import re
import subprocess
import uuid
import json
import glob
import time

import mss
import alphabetic_timestamp as ats

from . import log
from . import app_core
from . import merge

mini_tunner_file = ".mini.tunner"

def mkdir(arguments):
    cmd = MkdirCommand()
    cmd.run(arguments)


class MkdirCommand:
    def __init__(self):
        self.logger = logging.getLogger(app_core.AppCore.name)
        self.arguments = None
        self.directory_path = None
        self.dt = None
        self.tags = []
        self.variables = {}

    def run(self, arguments):
        self.arguments = arguments
        self.dt = datetime.datetime.now()
        self.tags = arguments.tags

        self.parse_variables()
        self.evaluate_directory_path()
        self.create_directory()
        self.create_tunner_file()
        self.create_subdirectories()

        self.logger.info(f"{self.id()} {self.directory_path}")

        self.open_explorer()
        self.copy_path_to_clipboard()
        self.switch_cwd()

    def parse_variables(self):
        for raw_variable in self.arguments.variables:
            if "=" in raw_variable:
                split_parts = raw_variable.split("=")
                self.variables[split_parts[0]] = split_parts[1]
            else:
                self.logger.warning(f"Variable {raw_variable} skipped")

    def create_directory(self):
        os.makedirs(self.directory_path, exist_ok=True)

    def create_subdirectories(self):
        for subdir in self.arguments.sub_directories:
            path = os.path.join(self.directory_path, subdir)
            os.makedirs(path, exist_ok=True)


    def create_tunner_file(self):
        content = {
            "test.run.id": self.id(),
            "time": str(self.dt),
            "variables": self.variables,
            "tags": self.tags,
            "local.machine": self.local_machine_detail()
        }

        with open(self.mini_tunner_file_path(), "w+") as file:
            json.dump(content, file, indent=4)

    def id(self):
        return ats.base62.from_datetime(self.dt, time_unit=ats.TimeUnit.seconds)

    def mini_tunner_file_path(self):
        return os.path.join(self.directory_path, mini_tunner_file)

    def local_machine_detail(self):
        return {
            "platform": platform.system(),
            "platform.release": platform.release(),
            "platform.version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": socket.gethostname(),
            "ip.address": socket.gethostbyname(socket.gethostname()),
            "mac.address": ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        }

    def evaluate_directory_path(self):
        self.directory_path = self.arguments.path_template
        self.evaluate_directory_path_datetime()
        self.evaluate_directory_path_variables()

    def evaluate_directory_path_datetime(self):
        self.directory_path = self.dt.strftime(self.directory_path)

    def evaluate_directory_path_variables(self):
        for key in self.variables:
            self.directory_path = self.directory_path.replace("{%s}" % key, self.variables[key])

    def open_explorer(self):
        if self.arguments.explorer:
            subprocess.Popen([f"explorer", f"{self.directory_path}"])

    def switch_cwd(self):
        if self.arguments.switch_cwd:
            os.chdir(self.directory_path)
            subprocess.run(["cmd"])

    def copy_path_to_clipboard(self):
        if self.arguments.copy_path_to_clipboard:
            # echo = subprocess.Popen(('echo', self.directory_path), stdout=subprocess.PIPE)
            # output = subprocess.check_output('clip', stdin=echo.stdout)
            # echo.wait()
            cmd = f"echo '{self.directory_path}' | clip"
            echo_clip = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = echo_clip.communicate()[0]

def ps(arguments):
    cmd = PrintScreenCommand()
    cmd.run(arguments)


class PrintScreenCommand:
    def __init__(self):
        self.logger = logging.getLogger(log.logger_name)
        self.arguments = None

    def run(self, arguments):
        self.arguments = arguments
        time.sleep(int(self.arguments.wait))

        path = self.file_path()
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)

        with mss.mss() as sct:
            sct.shot(mon=int(self.arguments.monitor), output=path)
            self.logger.debug(path)

    def file_path(self):
        path = ""
        if self.arguments.cwd:
            path = self.arguments.file_template
        else:
            last_tuner_directory = self.find_last_tunner_directory()
            path = os.path.join(last_tuner_directory, self.arguments.file_template)

        path = datetime.datetime.now().strftime(path)
        path = path.replace("{specific}", self.arguments.specific)
        return f"{path}.png"


    def find_last_tunner_directory(self):
        template = os.path.join(self.arguments.tunner_main_directory, "**", ".mini.tunner")
        index = {}
        for mini_tunner_file in glob.glob(template, recursive=True):
            index[mini_tunner_file] = self.read_tunner_file_time(mini_tunner_file)

        sorted_index = dict(sorted(index.items(), key=lambda item: item[1]))
        last_tunner_file = list(sorted_index.keys())[-1]
        return os.path.dirname(last_tunner_file)

    def read_tunner_file_time(self, path):
        content = self.read_tunner_file(path)
        return content["time"]

    def read_tunner_file(self, path):
        with open(path, "r") as file:
            return json.load(file)


def merge_all(arguments):
    cmd = merge.MergeCommand()
    cmd.run(arguments)



