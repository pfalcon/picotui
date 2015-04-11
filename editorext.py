#
# Extended VT100 terminal text editor, etc. widgets
# Copyright (c) 2015 Paul Sokolovsky
# Distributed under MIT License
#
import sys
import os
from editor import *


KEY_ESC = 20
KEY_F1 = 30

KEYMAP[b"\x1b"] = KEY_ESC
KEYMAP[b'\x1bOP'] = KEY_F1

# Edit single line, quit on Enter/Esc
class LineEditor(Editor):

    def handle_cursor_keys(self, key):
        if super().handle_cursor_keys(key):
            self.just_started = False
            return True
        return False

    def handle_key(self, key):
        if key in (KEY_ENTER, KEY_ESC):
            return key
        if self.just_started:
            # Overwrite initial string with new content
            self.set_lines([""])
            self.col = 0
            self.just_started = False

        return super().handle_key(key)

    def edit(self, line):
        self.set_lines([line])
        self.col = len(line)
        self.just_started = True
        key = self.loop()
        if key == KEY_ENTER:
            return self.content[0]
        return None


class Viewer(Editor):

    def handle_key(self, key):
        if key in (KEY_ENTER, KEY_ESC):
            return key


class EditorExt(Editor):

    def get_cur_line(self):
        return self.content[self.cur_line]

    def goto_line(self, no, center=True):
        if center:
            c = self.height // 2
            if no > c:
                self.top_line = no - c
                self.row = c
            else:
                self.top_line = 0
                self.row = no
        else:
            self.top_line = no
            self.row = 0
        self.cur_line = no
        self.update_screen()

    def draw_box(self, left, top, width, height):
        # Use http://www.utf8-chartable.de/unicode-utf8-table.pl
        # for utf-8 pseudographic reference
        bottom = top + height - 1
        self.goto(top, left)
        # "┌"
        self.wr(b"\xe2\x94\x8c")
        # "─"
        hor = b"\xe2\x94\x80" * (width - 2)
        self.wr(hor)
        # "┐"
        self.wr(b"\xe2\x94\x90")

        self.goto(bottom, left)
        # "└"
        self.wr(b"\xe2\x94\x94")
        self.wr(hor)
        # "┘"
        self.wr(b"\xe2\x94\x98")

        top += 1
        while top < bottom:
            # "│"
            self.goto(top, left)
            self.wr(b"\xe2\x94\x82")
            self.goto(top, left + width - 1)
            self.wr(b"\xe2\x94\x82")
            top += 1

    def clear_box(self, left, top, width, height):
        # doesn't work
        #self.wr("\x1b[%s;%s;%s;%s$z" % (top + 1, left + 1, top + height, left + width))
        s = b" " * width
        bottom = top + height - 1
        while top < bottom:
            self.goto(top, left)
            self.wr(s)
            top += 1

    def dialog_box(self, left, top, width, height, title=""):
        self.clear_box(left + 1, top + 1, width - 2, height - 2)
        self.draw_box(left, top, width, height)
        if title:
            #pos = (width - len(title)) / 2
            pos = 1
            self.goto(top, left + pos)
            self.wr(title)

    def dialog_edit_line(self, left=10, top=8, width=40, height=3, line="", title=""):
        self.dialog_box(left, top, width, height, title)
        e = LineEditor(left + 1, top + 1, width - 2, height - 2)
        return e.edit(line)


if __name__ == "__main__":

    with open(sys.argv[1]) as f:
        content = f.read().splitlines()
        #content = f.readlines()


#os.write(1, b"\x1b[18t")
#key = os.read(0, 32)
#print(repr(key))

#key = os.read(0, 32)
#print(repr(key))
#1/0

    e = EditorExt(left=1, top=1, width=60, height=25)
    e.init_tty()
    e.enable_mouse()

    s = e.dialog_edit_line(10, 5, 40, 3, title="Enter name:", line="test")
    e.cls()
    e.deinit_tty()
    print()
    print(s)

    1/0

#    e.cls()
    e.draw_box(0, 0, 62, 27)
    e.set_lines(content)
    e.loop()
    e.deinit_tty()
