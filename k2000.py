import random
import time

default_color = 127

def locate_knob(bank, line, col):
    knob = ((bank - 1) * 16) + ((line - 1) * 4) + (col - 1)
    return knob

def initialize_mf(out, bank):
    for i in xrange(16):
        out.write_short(0xb1, ((bank - 1) * 16) + i, default_color)

def rainbow(out, bank, line, col):
    b = locate_knob(bank, line, col)
    out.write_short(0xb2, b, 127)

def cut(out, bank, line, col):
    b = locate_knob(bank, line, col)
    out.write_short(0xb2, b, 0)
    out.write_short(0xb1, b, default_color)

def blink(out, bank, line, col, color, strobe):
    b = locate_knob(bank, line, col)
    out.write_short(0xb1, b, color)
    out.write_short(0xb2, b, strobe)

def dial(out, bank, line, col, num):
    b = locate_knob(bank, line, col)
    out.write_short(0xb0, b, num)


def kit(out, bank, line, color, stop):
    while True:
        for i in xrange(4):
            out.write_short(0xb1, i + ((bank - 1) * 16) + ((line - 1) * 4), color)
            attente = 0.1
            time.sleep(attente)
            out.write_short(0xb1, i + ((bank - 1) * 16) + ((line - 1) * 4), default_color)
        if stop():
            for i in xrange(4):
                out.write_short(0xb1, i + ((bank - 1) * 16) + ((line - 1) * 4), default_color)
            break

def auto(out, bank, line, col, stop):
    while True:
        for i in xrange(0, 127, 3):
            dial(out, bank, line, col, i)
            time.sleep(0.01)
        for i in xrange(127, 0, -3):
            dial(out, bank, line, col, i)
            time.sleep(0.05)
        if stop():
            dial(out, bank, line, col, 0)
            break

