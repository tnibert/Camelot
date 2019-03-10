import logging
import traceback


def return_def_logger(name):
    return return_logger(name, "/var/log/www-data/spam.log")


def return_ex_logger(name):
    return return_logger(name, "/var/log/www-data/exceptions.log")


def return_logger(name, fname):
    log = logging.getLogger(name)
    log.setLevel(logging.ERROR)
    fh = logging.FileHandler(fname)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    log.addHandler(fh)
    return log


def log_msg():
    pass


def log_exception(origin, ex):
    """
    Log an exception
    :param origin: pass in the __name__ of the calling module
    :param ex: pass in the exception
    :return: True on success, False on failure
    """
    # log the exception
    try:
        log = return_ex_logger(origin)
        traceback_str = "".join(traceback.format_tb(ex.__traceback__))
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        log.error(message + "\n" + traceback_str)
    except Exception as e:
        return False
    return True
