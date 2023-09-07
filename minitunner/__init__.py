import argparse
import logging
import logging.config
import os.path

from . import cli
from . import log
from . import app_core

def main():

    ac = app_core.AppCore()
    ac.set_standard_logger()

    parser = argparse.ArgumentParser(
        description=f"{ac.name}\n\n{ac.read_extended_help()}",
        formatter_class=argparse.RawTextHelpFormatter
    )

    mkdir_default_path = os.path.join(
        ac.app_directory(),
        "evidence",
        "%Y.%m.%d",
        "%Y.%m.%d_%H-%M-%S_{test.id}"
    )

    subparsers = parser.add_subparsers()

    mkdir_parser = subparsers.add_parser('mkdir')
    mkdir_parser.set_defaults(func=cli.mkdir)
    mkdir_parser.add_argument("-p", "--path-template", default=mkdir_default_path)
    mkdir_parser.add_argument("-t", "--tags", default=[], nargs='*')
    mkdir_parser.add_argument("-v", "--variables", default=["project="], nargs='*')
    mkdir_parser.add_argument("-s", "--sub-directories", default=[], nargs='*')
    mkdir_parser.add_argument("-e", "--explorer", action='store_true')
    mkdir_parser.add_argument("-w", "--switch_cwd", action='store_true')
    mkdir_parser.add_argument("-c", "--copy_path_to_clipboard", action='store_true')

    add_record_parser = subparsers.add_parser('add')
    add_record_parser.set_defaults(func=cli.add)
    add_record_parser.add_argument("-p", "--path", default=cli.mini_tunner_file)
    add_record_parser.add_argument("-t", "--type", required=True)
    add_record_parser.add_argument("--tags", default=[], nargs='*')
    add_record_parser.add_argument("-v", "--variables", default=[], nargs='*')

    print_screen_parser = subparsers.add_parser('ps')
    print_screen_parser.add_argument("-t", "--file-template", default="print_screens/{specific}_%Y.%m.%d_%H-%M-%S")
    print_screen_parser.add_argument("-s", "--specific", default="")
    print_screen_parser.add_argument("-c", "--cwd", action='store_true')
    print_screen_parser.add_argument("-d", "--tunner-main-directory", default=os.path.join(ac.app_directory(), "evidence"))
    print_screen_parser.add_argument("-w", "--wait", default=0)
    print_screen_parser.add_argument("-m", "--monitor", default=0)
    print_screen_parser.set_defaults(func=cli.ps)

    merge_parser = subparsers.add_parser('merge')
    merge_parser.add_argument("-s", "--source", default=os.path.join(ac.app_directory(), "evidence"))
    merge_parser.add_argument("-d", "--destination", default=os.path.join(ac.app_directory(), "projects"))
    merge_parser.add_argument("-l", "--last_day", action='store_true')
    merge_parser.add_argument("-t", "--tunner_file", default=cli.mini_tunner_file)
    merge_parser.add_argument("-p", "--project_filter", default=".*")
    merge_parser.add_argument("-m", "--merge_cmd", default="")
    merge_parser.add_argument("-c", "--clean_cmd", default="")
    merge_parser.add_argument("-f", "--finish_cmd", default="")

    merge_parser.set_defaults(func=cli.merge_all)

    bind_parser = subparsers.add_parser('bind')
    bind_parser.set_defaults(func=cli.bind)


    arguments = parser.parse_args()
    arguments.func(arguments)
