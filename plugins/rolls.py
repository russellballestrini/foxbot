#!/usr/bin/env python3
from random import randint


def roll(quant, dmax):
    """Roll the dice and return results"""
    rolls = []
    for x in range(quant):  # Change from xrange() to range()
        rolls.append(randint(1, dmax))

    # Use f-string for better readability in Python 3
    result = f"{', '.join(map(str, rolls))} for a total of {sum(rolls)}"
    return result


def main(msg):
    try:
        quant, dmax = msg.lstrip("rolls ").split("d")
        quant, dmax = int(quant), int(dmax)
    except (ValueError, IndexError):
        if "d" in msg:
            return "usage example: /me rolls 2d6"
        return

    if quant > 100 or quant < 1:
        return "You must roll between 1 and 100 dice, /me rolls 2d6"
    if dmax > 1000:
        return "Dice cannot have more than 1000 sides!"

    return roll(quant, dmax)
