#
# Simple VT100 terminal text editor widget
# Copyright (c) 2015 Paul Sokolovsky
# Distributed under MIT License
#
import sys
import os

from screen import *


class Editor(Screen):

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
        self.kbuf = b""

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

    def redraw(self):
        self.cursor(False)
        i = self.top_line
        r = self.top
        for c in range(self.height):
            self.goto(r, self.left)
            if i == self.total_lines:
                self.clear_num_pos(self.width)
            else:
                self.show_line(self.content[i], i)
                i += 1
            r += 1
        self.set_cursor()
        self.cursor(True)

    def update_line(self):
        self.cursor(False)
        self.goto(self.row + self.top, self.left)
        self.show_line(self.content[self.cur_line], self.cur_line)
        self.set_cursor()
        self.cursor(True)

    def show_line(self, l, i):
        l = l[self.margin:]
        l = l[:self.width]
        self.wr(l)
        self.clear_num_pos(self.width - len(l))

    def next_line(self):
        if self.row + 1 == self.height:
            self.top_line += 1
            return True
            self.redraw()
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
                    self.redraw()
                else:
                    self.set_cursor()
        elif key == KEY_UP:
            if self.cur_line > 0:
                self.cur_line -= 1
                redraw = self.adjust_cursor_eol()
                if self.row == 0:
                    if self.top_line > 0:
                        self.top_line -= 1
                        self.redraw()
                else:
                    self.row -= 1
                    if redraw:
                        self.redraw()
                    else:
                        self.set_cursor()
        elif key == KEY_LEFT:
            if self.col > 0:
                self.col -= 1
                self.set_cursor()
            elif self.margin > 0:
                self.margin -= 1
                self.redraw()
        elif key == KEY_RIGHT:
            self.col += 1
            if self.adjust_cursor_eol():
                self.redraw()
            else:
                self.set_cursor()
        elif key == KEY_HOME:
            self.col = 0
            if self.margin > 0:
                self.margin = 0
                self.redraw()
            else:
                self.set_cursor()
        elif key == KEY_END:
            self.col = len(self.content[self.cur_line])
            if self.adjust_cursor_eol():
                self.redraw()
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
            self.redraw()
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
            self.redraw()
        else:
            return False
        return True

    def handle_mouse(self, col, row):
        row -= self.top
        col -= self.left
        if 0 <= row < self.height and 0 <= col < self.width:
            self.row = row
            self.col = col
            self.cur_line = self.top_line + self.row
            self.adjust_cursor_eol()
            self.set_cursor()

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

    def handle_key(self, key):
        if key == KEY_QUIT:
            return key
        if self.handle_cursor_keys(key):
            return
        return self.handle_edit_key(key)

    def handle_edit_key(self, key):
            l = self.content[self.cur_line]
            if key == KEY_ENTER:
                self.content[self.cur_line] = l[:self.col + self.margin]
                self.cur_line += 1
                self.content[self.cur_line:self.cur_line] = [l[self.col + self.margin:]]
                self.total_lines += 1
                self.col = 0
                self.margin = 0
                self.next_line()
                self.redraw()
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

    def deinit_tty(self):
        # Don't leave cursor in the middle of screen
        self.goto(self.height, 0)
        super().deinit_tty()


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
