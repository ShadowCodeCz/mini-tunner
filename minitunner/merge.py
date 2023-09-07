import re
import glob
import json
import logging
import os.path
import shutil
import subprocess

from . import app_core

class TunnerFileMapper:
    def __init__(self):
        self.logger = logging.getLogger(app_core.AppCore.name)

    def map(self, working_directory, file_template, project_filter):
        result = {}

        template = os.path.join(working_directory, "**", file_template)
        self.logger.debug(f"TunnerFileMapper: template={template}")
        files = glob.glob(template, recursive=True)

        for file in set(files):
            self.logger.debug(f"TunnerFileMapper: \t located file={file}")
            try:
                content = self.read_tunner_file(file)
                project = self.read_project(content)

                if re.match(project_filter, project):
                    trid = content["test.run.id"]
                    content["file.path"] = file
                    result[trid] = content
            except Exception as e:
                self.logger.error(f"Parsing mini tunner file '{file}' failed. {e}")

        return result

    def read_project(self, content, default="other"):
        try:
            return content["variables"]["project"]
        except Exception as e:
            return default

    def read_tunner_file(self, file):
        with open(file, "r") as f:
            return json.load(f)


class MergeCommand:
    def __init__(self):
        self.arguments = None
        self.logger = logging.getLogger(app_core.AppCore.name)

    def run(self, arguments):
        self.arguments = arguments

        tunner_mapper = TunnerFileMapper()

        source_files = tunner_mapper.map(self.source(), self.arguments.tunner_file, self.arguments.project_filter)
        destination_files = tunner_mapper.map(arguments.destination, self.arguments.tunner_file, self.arguments.project_filter)

        for trid, content in source_files.items():
            self.logger.debug(f"MergeCommand: Process TRID={trid}")
            if not trid in destination_files:
                source_directory = os.path.dirname(content["file.path"])
                destination_directory = os.path.join(
                    self.arguments.destination,
                    self.project(content),
                    content["variables"]["test.id"].replace(" ", "_"),
                    content["time"].replace(" ", "_").replace(":", "-"),
                )
                os.makedirs(os.path.dirname(destination_directory), exist_ok=True)
                self.logger.info(f"src: {source_directory}\n"
                                 f"dst: {destination_directory}\n\n")
                shutil.copytree(source_directory, destination_directory)
                self.run_cmd(self.arguments.merge_cmd, destination_directory)
                self.run_cmd(self.arguments.clean_cmd, source_directory)
        self.run_cmd(self.arguments.finish_cmd, os.getcwd())

    def source(self):
        if self.arguments.last_day:
            sub_dirs = sorted([item for item in glob.glob(os.path.join(self.arguments.source, "*")) if os.path.isdir(item)])
            return sub_dirs[-1]
        else:
            return self.arguments.source

    def project(self, content, default="other"):
        try:
            return content["variables"]["project"].replace(" ", "_")
        except Exception as e:
            self.logger.error(f"Mini tunner file '{content['file.path']}' does not contain 'project' in 'variables'")
            return default

    def run_cmd(self, cmd, working_directory):
        original_wd = os.path.abspath(os.getcwd())
        os.chdir(working_directory)

        if cmd != None and cmd != "":
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            proc.communicate()
            proc.wait()

        os.chdir(original_wd)
