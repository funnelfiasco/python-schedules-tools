#!/usr/bin/env python
import argparse
import os
import sys
import re
import logging
from schedules_tools.converter import ScheduleConverter

logger = logging.getLogger(__name__)
handler_class_template = re.compile('^ScheduleHandler_(\S+)$')
VALID_MODULE_NAME = re.compile(r'^(\w+)\.py$', re.IGNORECASE)
BASE_DIR = os.path.dirname(os.path.realpath(
    os.path.join(__file__, os.pardir)))
PARENT_DIRNAME = os.path.basename(os.path.dirname(os.path.realpath(__file__)))

# FIXME(mpavlase): Figure out nicer way to deal with paths
sys.path.append(BASE_DIR)


def setup_logging(level):
    log_format = '%(name)-10s %(levelname)7s: %(message)s'
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)

    formatter = logging.Formatter(log_format)
    sh.setFormatter(formatter)

    # setup root logger
    inst = logging.getLogger('')
    inst.setLevel(level)
    inst.addHandler(sh)


def main(args):
    handlers_args_def = '--handlers-path',
    handlers_kwargs_def = {
        'help': 'Add path to discover handlers (needs to be python'
                ' module), can be called several times '
                '(conflicting names will be overriden - the last '
                'implementation will be used)',
        'action': 'append',
        'default': []
    }
    setup_logging(logging.DEBUG)
    converter = ScheduleConverter()

    # Separate parser to handle '--handlers-path' argument and prepare
    # converter.provided_exports to be used in main parser
    add_handler_parser = argparse.ArgumentParser(add_help=False)
    add_handler_parser.add_argument(*handlers_args_def, **handlers_kwargs_def)
    known_args = add_handler_parser.parse_known_args(args)

    opt_args = vars(known_args[0])  # 0. index contains successfully parsed args
    for path in opt_args.pop('handlers_path'):
        converter.add_discover_path(path)

    parser = argparse.ArgumentParser(description='Perform schedule conversions.')

    parser.add_argument(*handlers_args_def, **handlers_kwargs_def)

    parser.add_argument('-f', '--force',
                        help='Force target overwrite',
                        default=False,
                        action='store_true')

    parser.add_argument('--tj-id', metavar='TJ_PROJECT_ID',
                        help='TJ Project Id (e.g. rhel)')
    parser.add_argument('--major', help='Project major version number',
                        default='')
    parser.add_argument('--minor', help='Project minor version number',
                        default='')
    parser.add_argument('--maint', help='Project maint version number',
                        default='')
    parser.add_argument('--use-tji-file',
                        help='Use TJI file when exporting into TJP',
                        default=False,
                        action='store_true')

    parser.add_argument('--rally-iter', help='Rally iteration to import',
                        default='')

    parser.add_argument('--source-storage-format',
                        #choices=converter.handlers.keys(),
                        metavar='SRC_STORAGE_FORMAT',
                        help='Source storage format to use')
    parser.add_argument('--source-format',
                        choices=converter.handlers.keys(),
                        metavar='SRC_FORMAT',
                        help='Source format to enforce')
    parser.add_argument('source',
                        help='Source handle (file/URL/...)',
                        type=str,
                        metavar='SRC')

    parser.add_argument('target_format',
                        choices=converter.provided_exports,
                        metavar='TARGET_FORMAT',
                        help='Target format to convert')
    parser.add_argument('target', metavar='TARGET',
                        help='Output target', default=None, nargs='?')

    arguments = parser.parse_args(args)
    opt_args = vars(arguments)

    # --handlers-path argument is already procesed, it shouldn't be passed
    # as opt_args into handlers
    opt_args.pop('handlers_path')

    converter.import_schedule(arguments.source,
                              arguments.source_format,
                              handler_opt_args=opt_args)

    converter.export_schedule(arguments.target,
                              arguments.target_format,
                              handler_opt_args=opt_args)

if __name__ == '__main__':
    main(sys.argv[1:])
