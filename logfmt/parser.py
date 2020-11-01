# -*- coding: utf-8 -*-

from enum import Enum


class State(Enum):
    GARBAGE = 0
    KEY = 1
    EQUAL = 2
    IVALUE = 3
    QVALUE = 4


def check_char(c: str):
    return c > " " and c != '"' and c != "="


def eval_key(line: str, i: int, c: str, key: tuple, output: dict):
    state: State
    if check_char(c):
        state = State.KEY
        key += (c,)
    elif c == "=":
        output["".join(key).strip()] = True
        state = State.EQUAL
    else:
        output["".join(key).strip()] = True
        state = State.GARBAGE
    if i >= len(line):
        output["".join(key).strip()] = True
    return state, key, output


def eval_equal(
    line: str, i: int, c: str, key: tuple, value: tuple, escaped: bool, output: dict
):
    state: State
    if check_char(c):
        value = (c,)
        state = State.IVALUE
    elif c == '"':
        value = ()
        escaped = False
        state = State.QVALUE
    else:
        state = State.GARBAGE
    if i >= len(line):
        output["".join(key).strip()] = "".join(value) or True
    return state, value, escaped, output


def eval_ivalue(line: str, i: int, c: str, key: tuple, value: tuple, output: dict):
    state: State = State.IVALUE
    if not check_char(c):
        output["".join(key).strip()] = "".join(value)
        state = State.GARBAGE
    else:
        value += (c,)
    if i >= len(line):
        output["".join(key).strip()] = "".join(value)
    return state, value, output


def eval_qvalue(c: str, key: tuple, value: tuple, escaped: bool, output: dict):
    state: State = State.QVALUE
    if c == "\\":
        escaped = True
    elif c == '"':
        if escaped:
            escaped = False
            value += (c,)
            return state, value, escaped, output
        output["".join(key).strip()] = "".join(value)
        state = State.GARBAGE
    else:
        value += (c,)
    return state, value, escaped, output


def parse_line(line):
    output = {}
    key, value = (), ()
    escaped = False
    state = State.GARBAGE
    for i, c in enumerate(line):
        i += 1
        if state == State.GARBAGE:
            if check_char(c):
                key = (c,)
                state = State.KEY
            continue
        if state == State.KEY:
            state, key, output = eval_key(line, i, c, key, output)
            continue
        if state == State.EQUAL:
            state, value, escaped, output = eval_equal(
                line, i, c, key, value, escaped, output
            )
            continue
        if state == State.IVALUE:
            state, value, output = eval_ivalue(line, i, c, key, value, output)
            continue
        if state == State.QVALUE:
            state, value, escaped, output = eval_qvalue(c, key, value, escaped, output)
            continue
    return output
