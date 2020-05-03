import os
import sys

from .screen import Screen

from .defs import KEYMAP as _KEYMAP, KEY_SCRLDN, KEY_SCRLUP

# Standard widget result actions (as return from .loop())
ACTION_OK = 1000
ACTION_CANCEL = 1001
ACTION_NEXT = 1002
ACTION_PREV = 1003

# Platform switch.
is_micropython = False
try:
    if sys.implementation.name == "micropython":
        is_micropython = True
except:
    pass


class Widget(Screen):

    def __init__(self):
        self.kbuf = b""
        self.signals = {}

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def inside(self, x, y):
        return self.y <= y < self.y + self.h and self.x <= x < self.x + self.w

    def signal(self, sig):
        if sig in self.signals:
            self.signals[sig](self)

    def on(self, sig, handler):
        self.signals[sig] = handler

    @staticmethod
    def longest(items):
        if not items:
            return 0
        return max((len(t) for t in items))

    def set_cursor(self):
        # By default, a widget doesn't use text cursor, so disables it
        self.cursor(False)

    def get_input(self):
        if self.kbuf:
            key = self.kbuf[0:1]
            self.kbuf = self.kbuf[1:]
        else:
            key = os.read(0, 32)
            if key[0] != 0x1b:
                key = key.decode()
                self.kbuf = key[1:].encode()
                key = key[0:1].encode()
        key = _KEYMAP.get(key, key)

        if isinstance(key, bytes) and key.startswith(b"\x1b[M") and len(key) == 6:
            row = key[5] - 33
            col = key[4] - 33
            return [col, row]

        return key

    def get_input_micropython(self):

        # Read from interface/keyboard one byte each and match against function keys.
        # https://github.com/robert-hh/Micropython-Editor/blob/master/pye.py

        # Collect key strokes.
        in_buffer = self.rd()

        # When it's starting with ESC, it must be fct.
        if in_buffer == '\x1b':
            while True:
                in_buffer += self.rd()

                # Double ESC for the rescue.
                if in_buffer == '\x1b\x1b':
                    in_buffer = '\x1b'
                    break

                c = in_buffer[-1]
                if c == '~' or (c.isalpha() and c != 'O'):
                    break

        # Use bytes representation.
        keys = bytes(in_buffer, None)

        # FIXME: Special handling for mice.
        # Read 3 more characters.
        if in_buffer.startswith('\x1b[M'):
            mouse_fct = ord(self.rd())
            mouse_x = ord(self.rd()) - 33
            mouse_y = ord(self.rd()) - 33
            if mouse_fct == 0x61:
                return KEY_SCRLDN, 3
            elif mouse_fct == 0x60:
                return KEY_SCRLUP, 3
            else:
                # Set the cursor.
                return [mouse_x, mouse_y]

        # Resolve key.
        elif keys in _KEYMAP:
            key = _KEYMAP[keys]
            return key

        # This is just plain text.
        elif ord(in_buffer[0]) >= 32:
            return in_buffer

        return keys

    def handle_input(self, inp):
        if isinstance(inp, list):
            res = self.handle_mouse(inp[0], inp[1])
        else:
            res = self.handle_key(inp)
        return res

    def loop(self):
        self.redraw()
        while True:
            if is_micropython:
                key = self.get_input_micropython()
            else:
                key = self.get_input()
            res = self.handle_input(key)

            if res is not None and res is not True:
                return res


class FocusableWidget(Widget):
    # If set to non-False, pressing Enter on this widget finishes
    # dialog, with Dialog.loop() return value being this value.
    finish_dialog = False


class EditableWidget(FocusableWidget):

    def get(self):
        raise NotImplementedError


class ChoiceWidget(EditableWidget):

    def __init__(self, choice):
        super().__init__()
        self.choice = choice

    def get(self):
        return self.choice


# Widget with few internal selectable items
class ItemSelWidget(ChoiceWidget):

    def __init__(self, items):
        super().__init__(0)
        self.items = items

    def move_sel(self, direction):
        self.choice = (self.choice + direction) % len(self.items)
        self.redraw()
        self.signal("changed")
