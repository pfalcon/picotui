#
# Extended VT100 terminal text editor, etc. widgets
# Copyright (c) 2015 Paul Sokolovsky
# Distributed under MIT License
#
import sys
import os
from .editor import *


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
        self.adjust_cursor_eol()
        self.just_started = True
        key = self.loop()
        if key == KEY_ENTER:
            return self.content[0]
        return None


class Viewer(Editor):

    def handle_key(self, key):
        if key in (KEY_ENTER, KEY_ESC):
            return key
        if super().handle_cursor_keys(key):
            return True


# Viewer with colored lines, (whole line same color)
class LineColorViewer(Viewer):

    def show_line(self, l, i):
        if self.is_dict_color:
            c = self.lines_c.get(i, self.def_c)
        else:
            try:
                c = self.lines_c[i]
            except IndexError:
                c = self.def_c
        self.attr_color(c)
        super().show_line(l, i)
        self.attr_reset()

    def set_line_colors(self, default_color, color_list={}):
        self.def_c = default_color
        self.lines_c = color_list
        self.is_dict_color = isinstance(color_list, dict)


# Viewer with color support, (echo line may consist of spans
# of different colors)
class CharColorViewer(Viewer):

    def show_line(self, l, i):
        # TODO: handle self.margin, self.width
        length = 0
        for span in l:
            if isinstance(span, tuple):
                span, c = span
            else:
                c = self.def_c
            self.attr_color(c)
            self.wr(span)
            length += len(span)
        self.attr_color(self.def_c)
        self.clear_num_pos(self.width - length)
        self.attr_reset()

    def set_def_color(self, default_color):
        self.def_c = default_color


class EditorExt(Editor):

    screen_width = 80

    def __init__(self, left=0, top=0, width=80, height=24):
        super().__init__(left, top, width, height)
        # +1 assumes there's a border around editor pane
        self.status_y = top + height + 1

    def get_cur_line(self):
        return self.content[self.cur_line]

    def line_visible(self, no):
        return self.top_line <= no < self.top_line + self.height

    # If line "no" is already on screen, just reposition cursor to it and
    # return False. Otherwise, show needed line either at the center of
    # screen or at the top, and return True.
    def goto_line(self, no, col=None, center=True):
        self.cur_line = no

        if self.line_visible(no):
            self.row = no - self.top_line
            if col is not None:
                self.col = col
                if self.adjust_cursor_eol():
                    self.redraw()
            self.set_cursor()
            return False

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

        if col is not None:
            self.col = col
            self.adjust_cursor_eol()
        self.redraw()
        return True

    def show_status(self, msg):
        self.cursor(False)
        self.goto(0, self.status_y)
        self.wr(msg)
        self.clear_to_eol()
        self.set_cursor()
        self.cursor(True)

    def show_cursor_status(self):
        self.cursor(False)
        self.goto(0, 31)
        self.wr("% 3d:% 3d" % (self.cur_line, self.col + self.margin))
        self.set_cursor()
        self.cursor(True)

    def dialog_edit_line(self, left=None, top=8, width=40, height=3, line="", title=""):
        if left is None:
            left = (self.screen_width - width) / 2
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
