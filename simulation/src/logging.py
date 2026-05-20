import datetime
import logging
import os
import sys


class Log(object):
    def __init__(self):
        pass

    def _create_log(self, log_file_name):
        log = logging.getLogger(__name__)
        log.setLevel(logging.DEBUG)
        if os.path.isfile(log_file_name):
            temp_handler = logging.StreamHandler(sys.stderr)
            temp_handler.setLevel(logging.WARNING)
            log.addHandler(temp_handler)
            log.warning(
                "Log file " + log_file_name + " exists and will be overwritten."
            )
            log.removeHandler(temp_handler)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file_name, mode="w+")
        file_handler.setLevel(logging.DEBUG)
        log.addHandler(file_handler)
        log.addHandler(stderr_handler)
        log.info("Execution Time : " + str(datetime.datetime.now()))
        log.debug("Command line: python " + " ".join(sys.argv[0:]) + "\n\n")
        log.debug("Warnings and Errors:\n")
        return log

    def _log_args(self, log, arg_list, protein_sequence=None):
        log.debug("\n\nList of Parameters:")
        if protein_sequence is not None:
            log.debug("Protein Sequence : " + protein_sequence)
        for k in arg_list:
            log.debug(k + " : " + str(arg_list[k]))
        log.debug("\n\n")
