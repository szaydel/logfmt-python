# -*- coding: utf-8 -*-

from enum import Enum


class State(Enum):
    GARBAGE = 0
    KEY = 1
    EQUAL = 2
    IVALUE = 3
    QVALUE = 4


class ParserState:
    def __init__(self):
        self.output = {}
        self.key = ()
        self.value = ()
        self.escaped = False
        self.state = State.GARBAGE


def check_char(c: str):
    return c > " " and c != '"' and c != "="


def eval_key(line: str, i: int, c: str, p: ParserState):
    if check_char(c):
        p.state = State.KEY
        p.key += (c,)
    elif c == "=":
        p.output["".join(p.key).strip()] = True
        p.state = State.EQUAL
    else:
        p.output["".join(p.key).strip()] = True
        p.state = State.GARBAGE
    if i >= len(line):
        p.output["".join(p.key).strip()] = True


def eval_equal(
    line: str, i: int, c: str, p: ParserState):
    if check_char(c):
        p.value = (c,)
        p.state = State.IVALUE
    elif c == '"':
        p.value = ()
        p.escaped = False
        p.state = State.QVALUE
    else:
        p.state = State.GARBAGE
    if i >= len(line):
        p.output["".join(p.key).strip()] = "".join(p.value) or True


def eval_ivalue(line: str, i: int, c: str, p: ParserState):
    if not check_char(c):
        p.output["".join(p.key).strip()] = "".join(p.value)
        p.state = State.GARBAGE
    else:
        p.value += (c,)
    if i >= len(line):
        p.output["".join(p.key).strip()] = "".join(p.value)


def eval_qvalue(line: str, i: int, c: str, p: ParserState):
    _, _ = line, i
    if c == "\\":
        p.escaped = True
    elif c == '"':
        if p.escaped:
            p.escaped = False
            p.value += (c,)
            return
        p.output["".join(p.key).strip()] = "".join(p.value)
        p.state = State.GARBAGE
    else:
        p.value += (c,)
    return


def parse_line(line):
    p = ParserState()
    for i, c in enumerate(line):
        i += 1
        if p.state == State.GARBAGE:
            if check_char(c):
                p.key = (c,)
                p.state = State.KEY
            continue
        if p.state == State.KEY:
            eval_key(line, i, c, p)
            continue
        if p.state == State.EQUAL:
            eval_equal(
                line, i, c, p)
            continue
        if p.state == State.IVALUE:
            eval_ivalue(line, i, c, p)
            continue
        if p.state == State.QVALUE:
            eval_qvalue(line, i, c, p)
            continue
    return p.output
