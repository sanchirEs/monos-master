""" common tags """
import math
from django import template

register = template.Library()

@register.filter(name='add')
def add(value, arg):
    """ add filter """

    summmary = 0

    try:

        augend = int(value)

        addend = int(arg)

        summmary = augend + addend

    except  ValueError:

        pass

    return summmary


@register.filter(name='subtract')
def subtract(value, arg):
    """ subtract filter """

    diff = 0

    try:

        minuend = int(value)

        subtrahend = int(arg)

        diff = minuend - subtrahend

    except  ValueError:

        pass

    return diff


@register.filter(name='multiply')
def multiply(value, arg):
    """ multiply filter """

    product = 0

    try:

        multiplicand = int(value)

        multiplier = int(arg)

        product = multiplicand * multiplier

    except  ValueError:

        pass

    return product


@register.filter(name='divide')
def divide(value, arg):
    """ division filter """

    quotient = 0

    try:

        dividend = int(value)

        divisor = int(arg)

        quotient = int(dividend / divisor)

    except  (ValueError, ZeroDivisionError):

        pass

    return quotient

@register.filter(name='xp_to_nextlevel')
def xp_to_nextlevel(value, arg):
    """ xp next filter """

    quotient = 0

    try:

        current_xp = int(value)

        current_level = int(arg)

        quotient = int(2**(current_level-1)-1)*200+100-current_xp

    except  (ValueError, ZeroDivisionError):

        pass

    return quotient

@register.filter(name='xp_to_percent')
def xp_to_percent(value, arg):
    """ xp percent filter """

    quotient = 0

    try:

        current_xp = int(value)

        current_level = int(arg)

        quotient = int(2**(current_level-1)-1)*200+100

        quotient = math.floor((current_xp/quotient)*100)

    except  (ValueError, ZeroDivisionError):

        pass

    return quotient

@register.filter(name='percent')
def percent(value, arg):
    """ percent filter """

    quotient = 0

    try:

        a = int(value)

        b = int(arg)

        quotient = math.floor((a/b)*100)

    except  (ValueError, ZeroDivisionError):

        pass

    return quotient

@register.filter(name='reward')
def reward(value):
    """ reward moil """

    quotient = 0

    try:

        a = int(value)

        quotient = 2**(a-1)

    except  (ValueError, ZeroDivisionError):

        pass

    return quotient