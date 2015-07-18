import os

from screen import *


class Widget(Screen):

    focusable = False

    def __init__(self):
        self.kbuf = b""

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def inside(self, x, y):
        return self.y <= y < self.y + self.h and self.x <= x < self.x + self.w

    def get_input(self):
        if self.kbuf:
            key = self.kbuf[0:1]
            self.kbuf = self.kbuf[1:]
        else:
            key = os.read(0, 32)
            if key[0] != 0x1b:
                self.kbuf = key[1:]
                key = key[0:1]
        key = KEYMAP.get(key, key)
        return key

    def loop(self):
        self.redraw()
        while True:
            key = self.get_input()
            if isinstance(key, bytes) and key.startswith(b"\x1b[M") and len(key) == 6:
                row = key[5] - 33
                col = key[4] - 33
                res = self.handle_mouse(col, row)
            else:
                res = self.handle_key(key)

            if res is not None:
                return res
