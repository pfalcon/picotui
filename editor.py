#
# Simple VT100 terminal text editor widget
# Copyright (c) 2015 Paul Sokolovsky
# Distributed under MIT License
#
import sys
import os


KEY_UP = 1
KEY_DOWN = 2
KEY_LEFT = 3
KEY_RIGHT = 4
KEY_HOME = 5
KEY_END = 6
KEY_PGUP = 7
KEY_PGDN = 8
KEY_QUIT = 9
KEY_ENTER = 10
KEY_BACKSPACE = 11
KEY_DELETE = 12

KEYMAP = {
b"\x1b[A": KEY_UP,
b"\x1b[B": KEY_DOWN,
b"\x1b[D": KEY_LEFT,
b"\x1b[C": KEY_RIGHT,
b"\x1bOH": KEY_HOME,
b"\x1bOF": KEY_END,
b"\x1b[1~": KEY_HOME,
b"\x1b[4~": KEY_END,
b"\x1b[5~": KEY_PGUP,
b"\x1b[6~": KEY_PGDN,
b"\x03": KEY_QUIT,
b"\r": KEY_ENTER,
b"\x7f": KEY_BACKSPACE,
b"\x1b[3~": KEY_DELETE,
}


class Editor:

    def __init__(self, left=0, top=0, width=80, height=24):
        self.top_line = 0
        self.cur_line = 0
        self.row = 0
        self.col = 0
        self.left = left
        self.top = top
        self.height = height
        self.width = width
        self.margin = 0

    def enable_mouse(self):
        # Mouse reporting - X10 compatbility mode
        os.write(1, b"\x1b[?9h")

    @staticmethod
    def wr(s):
        # TODO: When Python is 3.5, update this to use only bytes
        if isinstance(s, str):
            s = bytes(s, "utf-8")
        os.write(1, s)

    @staticmethod
    def cls():
        Editor.wr(b"\x1b[2J")

    @staticmethod
    def goto(row, col):
        # TODO: When Python is 3.5, update this to use bytes
        Editor.wr("\x1b[%d;%dH" % (row + 1, col + 1))

    @staticmethod
    def clear_to_eol():
        Editor.wr(b"\x1b[0K")

    # Clear specified number of positions
    @staticmethod
    def clear_num_pos(num):
        if num > 0:
            Editor.wr("\x1b[%dX" % num)

    @staticmethod
    def cursor(onoff):
        if onoff:
            Editor.wr(b"\x1b[?25h")
        else:
            Editor.wr(b"\x1b[?25l")

    def set_cursor(self):
        self.goto(self.row + self.top, self.col + self.left)

    def adjust_cursor_eol(self):
        # Returns True if entire window needs redraw
        val = self.col + self.margin
        val = min(val, len(self.content[self.cur_line]))
        if val > self.width - 1:
            self.margin = val - (self.width - 1)
            self.col = self.width - 1
            return True
        else:
            self.col = val - self.margin
            return False

    def set_lines(self, lines):
        self.content = lines
        self.total_lines = len(lines)

    def update_screen(self):
        self.cursor(False)
        i = self.top_line
        r = self.top
        for c in range(self.height):
            self.goto(r, self.left)
            if i == self.total_lines:
                self.clear_num_pos(self.width)
            else:
                self.show_line(self.content[i])
                i += 1
            r += 1
        self.set_cursor()
        self.cursor(True)

    def update_line(self):
        self.cursor(False)
        self.goto(self.row + self.top, self.left)
        self.show_line(self.content[self.cur_line])
        self.set_cursor()
        self.cursor(True)

    def show_line(self, l):
        l = l[self.margin:]
        l = l[:self.width]
        self.wr(l)
        self.clear_num_pos(self.width - len(l))

    def next_line(self):
        if self.row + 1 == self.height:
            self.top_line += 1
            return True
            self.update_screen()
        else:
            self.row += 1
            return False
            self.set_cursor()

    def handle_cursor_keys(self, key):
        if key == KEY_DOWN:
            if self.cur_line + 1 != self.total_lines:
                self.cur_line += 1
                redraw = self.adjust_cursor_eol()
                if self.next_line() or redraw:
                    self.update_screen()
                else:
                    self.set_cursor()
        elif key == KEY_UP:
            if self.cur_line > 0:
                self.cur_line -= 1
                redraw = self.adjust_cursor_eol()
                if self.row == 0:
                    if self.top_line > 0:
                        self.top_line -= 1
                        self.update_screen()
                else:
                    self.row -= 1
                    if redraw:
                        self.update_screen()
                    else:
                        self.set_cursor()
        elif key == KEY_LEFT:
            if self.col > 0:
                self.col -= 1
                self.set_cursor()
            elif self.margin > 0:
                self.margin -= 1
                self.update_screen()
        elif key == KEY_RIGHT:
            self.col += 1
            if self.adjust_cursor_eol():
                self.update_screen()
            else:
                self.set_cursor()
        elif key == KEY_HOME:
            self.col = 0
            if self.margin > 0:
                self.margin = 0
                self.update_screen()
            else:
                self.set_cursor()
        elif key == KEY_END:
            self.col = len(self.content[self.cur_line])
            if self.adjust_cursor_eol():
                self.update_screen()
            else:
                self.set_cursor()
        elif key == KEY_PGUP:
            self.cur_line -= self.height
            self.top_line -= self.height
            if self.top_line < 0:
                self.top_line = 0
                self.cur_line = 0
                self.row = 0
            elif self.cur_line < 0:
                self.cur_line = 0
                self.row = 0
            self.adjust_cursor_eol()
            self.update_screen()
        elif key == KEY_PGDN:
            self.cur_line += self.height
            self.top_line += self.height
            if self.cur_line >= self.total_lines:
                self.top_line = self.total_lines - self.height
                self.cur_line = self.total_lines - 1
                if self.top_line >= 0:
                    self.row = self.height - 1
                else:
                    self.top_line = 0
                    self.row = self.cur_line
            self.adjust_cursor_eol()
            self.update_screen()
        elif isinstance(key, bytes) and key.startswith(b"\x1b[M") and len(key) == 6:
            row = key[5] - 33
            col = key[4] - 33
            row -= self.top
            col -= self.left
            if 0 <= row < self.height and 0 <= col < self.width:
                self.row = row
                self.col = col
                self.cur_line = self.top_line + self.row
                self.adjust_cursor_eol()
                self.set_cursor()
        else:
            return False
        return True

    def loop(self):
        self.update_screen()
        while True:
            buf = os.read(0, 32)
            sz = len(buf)
            i = 0
            while i < sz:
                if buf[0] == 0x1b:
                    key = buf
                    i = len(buf)
                else:
                    key = buf[i:i + 1]
                    i += 1
                #self.show_status(repr(key))
                if key in KEYMAP:
                    key = KEYMAP[key]
                if key == KEY_QUIT:
                    return key
                if self.handle_cursor_keys(key):
                    continue
                res = self.handle_key(key)
                if res is not None:
                    return res

    def handle_key(self, key):
            l = self.content[self.cur_line]
            if key == KEY_ENTER:
                self.content[self.cur_line] = l[:self.col + self.margin]
                self.cur_line += 1
                self.content[self.cur_line:self.cur_line] = [l[self.col + self.margin:]]
                self.total_lines += 1
                self.col = 0
                self.margin = 0
                self.next_line()
                self.update_screen()
            elif key == KEY_BACKSPACE:
                if self.col + self.margin:
                    if self.col:
                        self.col -= 1
                    else:
                        self.margin -= 1
                    l = l[:self.col + self.margin] + l[self.col + self.margin + 1:]
                    self.content[self.cur_line] = l
                    self.update_line()
            elif key == KEY_DELETE:
                l = l[:self.col + self.margin] + l[self.col + self.margin + 1:]
                self.content[self.cur_line] = l
                self.update_line()
            else:
                l = l[:self.col + self.margin] + str(key, "utf-8") + l[self.col + self.margin:]
                self.content[self.cur_line] = l
                self.col += 1
                self.adjust_cursor_eol()
                self.update_line()

    @classmethod
    def init_tty(cls):
        import tty, termios
        cls.org_termios = termios.tcgetattr(0)
        tty.setraw(0)

    def deinit_tty(self):
        # Don't leave cursor in the middle of screen
        self.goto(self.height, 0)
        import termios
        termios.tcsetattr(0, termios.TCSANOW, self.org_termios)


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        content = f.read().splitlines()
        #content = f.readlines()


#os.write(1, b"\x1b[18t")
#key = os.read(0, 32)
#print(repr(key))

#key = os.read(0, 32)
#print(repr(key))

    e = Editor()
    e.init_tty()
    e.enable_mouse()
    e.set_lines(content)
    e.loop()
    e.deinit_tty()
