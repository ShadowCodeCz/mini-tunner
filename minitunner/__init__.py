import argparse
import logging
import logging.config

from . import cli
from . import log


def main():
    parser = argparse.ArgumentParser(
        description="Mini Tunner",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("-l", "--logger_level", default="DEBUG")
    subparsers = parser.add_subparsers()

    mkdir_parser = subparsers.add_parser('mkdir')
    mkdir_parser.set_defaults(func=cli.mkdir)
    mkdir_parser.add_argument("-p", "--path-template", default="C:\\evidence\\%Y.%m.%d\\%Y.%m.%d_%H-%M-%S_{test.id}\\")
    mkdir_parser.add_argument("-t", "--tags", default=[], nargs='*')
    mkdir_parser.add_argument("-v", "--variables", default=["project="], nargs='*')
    mkdir_parser.add_argument("-s", "--sub-directories", default=["subdir"], nargs='*')

    print_screen_parser = subparsers.add_parser('ps')
    print_screen_parser.add_argument("-t", "--file-template", default="print_screens/{specific}_%Y.%m.%d_%H-%M-%S")
    print_screen_parser.add_argument("-s", "--specific", default="")
    print_screen_parser.add_argument("-c", "--cwd", action='store_true')
    print_screen_parser.add_argument("-d", "--tunner-main-directory", default="C:\\evidence\\")
    print_screen_parser.add_argument("-w", "--wait", default=0)
    print_screen_parser.add_argument("-m", "--monitor", default=0)
    print_screen_parser.set_defaults(func=cli.ps)

    arguments = parser.parse_args()
    logging.config.dictConfig(log.default_logger_configuration(arguments.logger_level))
    arguments.func(arguments)

