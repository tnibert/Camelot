import logging


def return_def_logger(name):
    return return_logger(name, "spam.log")


def return_ex_logger(name):
    return return_logger(name, "exceptions.log")


def return_logger(name, fname):
    log = logging.getLogger(name)
    log.setLevel(logging.ERROR)
    fh = logging.FileHandler(fname)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    log.addHandler(fh)
    return log