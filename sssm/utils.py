'''
Created on 11 Apr 2018

@author: conor
'''

import time


def _micros_since_epoch():
    """ easily mockable implementation of micros_since_epoch for testing """
    return round((10 ** 6) * time.time())


def micros_since_epoch():
    """ return integer representing number of microseconds since epoch """
    return _micros_since_epoch()


def geometric_mean(ps):
    """ return geometric mean of values in ps
    
    @param ps - list of float or integer values
    """
    if not ps:
        return None

    x = ps[0]

    for p in ps[1:]:
        x *= p

    return x ** (1 / len(ps))


_auto_increment_value = 0


def auto_increment():
    """ return auto_incrementing integer """
    global _auto_increment_value
    _auto_increment_value += 1
    return _auto_increment_value - 1


def reset_auto_increment():
    """ reset auto incrementing integer to zero for testing """
    global _auto_increment_value
    _auto_increment_value = 0


def assert_true(cond, err):
    """ assert given condition is True otherwise raise given error
        
    @param cond - condition that must be true
    @param err - error message to raise if condition found to be False
    """

    if not cond:
        raise Error(err)


class Error(Exception):
    """ module error class """
