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
        self.map = {
            State.EQUAL: self.eval_equal,
            State.GARBAGE: self.eval_garbage,
            State.KEY: self.eval_key,
            State.IVALUE: self.eval_ivalue,
            State.QVALUE: self.eval_qvalue,
        }

    def eval_char(self, state: State, line: str, i: int, c: str):
        return self.map[state](line, i, c)

    @staticmethod
    def check_char(c: str):
        return c > " " and c != '"' and c != "="

    def eval_garbage(self, line: str, i: int, c: str):
        _, _ = line, i
        if self.check_char(c):
            self.key = (c,)
            self.state = State.KEY

    def eval_key(self, line: str, i: int, c: str):
        if self.check_char(c):
            self.state = State.KEY
            self.key += (c,)
        elif c == "=":
            self.output["".join(self.key).strip()] = True
            self.state = State.EQUAL
        else:
            self.output["".join(self.key).strip()] = True
            self.state = State.GARBAGE
        if i >= len(line):
            self.output["".join(self.key).strip()] = True

    def eval_equal(self, line: str, i: int, c: str):
        if self.check_char(c):
            self.value = (c,)
            self.state = State.IVALUE
        elif c == '"':
            self.value = ()
            self.escaped = False
            self.state = State.QVALUE
        else:
            self.state = State.GARBAGE
        if i >= len(line):
            self.output["".join(self.key).strip()] = "".join(self.value) or True

    def eval_ivalue(self, line: str, i: int, c: str):
        if not self.check_char(c):
            self.output["".join(self.key).strip()] = "".join(self.value)
            self.state = State.GARBAGE
        else:
            self.value += (c,)
        if i >= len(line):
            self.output["".join(self.key).strip()] = "".join(self.value)

    def eval_qvalue(self, line: str, i: int, c: str):
        _, _ = line, i
        if c == "\\":
            self.escaped = True
        elif c == '"':
            if self.escaped:
                self.escaped = False
                self.value += (c,)
                return
            self.output["".join(self.key).strip()] = "".join(self.value)
            self.state = State.GARBAGE
        else:
            self.value += (c,)
        return


def parse_line(line):
    p = ParserState()
    for i, c in enumerate(line):
        i += 1
        p.eval_char(p.state, line, i, c)
    return p.output
