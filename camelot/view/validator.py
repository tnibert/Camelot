class validate(object):
    """
    validation decorator
    """
    #def __init__(self):

    def __call__(self, f):
        #self.f(*args)

        def wrapped_f(*args):
            f(*args)

        return wrapped_f
