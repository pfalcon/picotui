import os


COLOR_BLACK    = 0
COLOR_RED      = 1
COLOR_GREEN    = 2
COLOR_YELLOW   = 3
COLOR_BLUE     = 4
COLOR_MAGENTA  = 5
COLOR_CYAN     = 6
COLOR_WHITE    = 7
ATTR_INTENSITY = 8
COLOR_GRAY     = COLOR_BLACK | ATTR_INTENSITY
COLOR_BRIGHT_RED      = COLOR_RED | ATTR_INTENSITY
COLOR_BRIGHT_GREEN    = COLOR_GREEN | ATTR_INTENSITY
COLOR_BRIGHT_YELLOW   = COLOR_YELLOW | ATTR_INTENSITY
COLOR_BRIGHT_BLUE     = COLOR_BLUE | ATTR_INTENSITY
COLOR_BRIGHT_MAGENTA  = COLOR_MAGENTA | ATTR_INTENSITY
COLOR_BRIGHT_CYAN     = COLOR_CYAN | ATTR_INTENSITY
COLOR_BRIGHT_WHITE    = COLOR_WHITE | ATTR_INTENSITY

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
KEY_TAB = b"\t"
KEY_SHIFT_TAB = b"\x1b[Z"
KEY_ESC = 20
KEY_F1 = 30
KEY_F2 = 31
KEY_F3 = 32
KEY_F4 = 33
KEY_F5 = b'\x1b[15~'
KEY_F6 = b'\x1b[17~'
KEY_F7 = b'\x1b[18~'
KEY_F8 = b'\x1b[19~'
KEY_F9 = b'\x1b[20~'
KEY_F10 = b'\x1b[21~'

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
b"\x1b": KEY_ESC,
b"\x1bOP": KEY_F1,
b"\x1bOQ": KEY_F2,
b"\x1bOR": KEY_F3,
b"\x1bOS": KEY_F4,
}

class Screen:

    @staticmethod
    def enable_mouse():
        # Mouse reporting - X10 compatibility mode
        os.write(1, b"\x1b[?9h")

    @staticmethod
    def wr(s):
        # TODO: When Python is 3.5, update this to use only bytes
        if isinstance(s, str):
            s = bytes(s, "utf-8")
        os.write(1, s)

    @staticmethod
    def wr_fixedw(s, width):
        # Write string in a fixed-width field
        s = s[:width]
        Screen.wr(s)
        Screen.wr(" " * (width - len(s)))
        # Doesn't work here, as it doesn't advance cursor
        #Screen.clear_num_pos(width - len(s))

    @staticmethod
    def cls():
        Screen.wr(b"\x1b[2J")

    @staticmethod
    def goto(x, y):
        # TODO: When Python is 3.5, update this to use bytes
        Screen.wr("\x1b[%d;%dH" % (y + 1, x + 1))

    @staticmethod
    def clear_to_eol():
        Screen.wr(b"\x1b[0K")

    # Clear specified number of positions
    @staticmethod
    def clear_num_pos(num):
        if num > 0:
            Screen.wr("\x1b[%dX" % num)

    @staticmethod
    def attr_color(fg, bg):
        # TODO: Switch to b"%d" % foo when py3.5 is everywhere
        if bg is None:
            if (fg > 8):
                Screen.wr("\x1b[%d;1m" % (fg + 30 - 8))
            else:
                Screen.wr("\x1b[%dm" % (fg + 30))
        else:
            assert bg <= 8
            if (fg > 8):
                Screen.wr("\x1b[%d;%d;1m" % (fg + 30 - 8, bg + 40))
            else:
                Screen.wr("\x1b[%d;%dm" % (fg + 30, bg + 40))

    @staticmethod
    def attr_reset():
        Screen.wr(b"\x1b[0m")

    @staticmethod
    def cursor(onoff):
        if onoff:
            Screen.wr(b"\x1b[?25h")
        else:
            Screen.wr(b"\x1b[?25l")

    def draw_box(self, left, top, width, height):
        # Use http://www.utf8-chartable.de/unicode-utf8-table.pl
        # for utf-8 pseudographic reference
        bottom = top + height - 1
        self.goto(left, top)
        # "┌"
        self.wr(b"\xe2\x94\x8c")
        # "─"
        hor = b"\xe2\x94\x80" * (width - 2)
        self.wr(hor)
        # "┐"
        self.wr(b"\xe2\x94\x90")

        self.goto(left, bottom)
        # "└"
        self.wr(b"\xe2\x94\x94")
        self.wr(hor)
        # "┘"
        self.wr(b"\xe2\x94\x98")

        top += 1
        while top < bottom:
            # "│"
            self.goto(left, top)
            self.wr(b"\xe2\x94\x82")
            self.goto(left + width - 1, top)
            self.wr(b"\xe2\x94\x82")
            top += 1

    def clear_box(self, left, top, width, height):
        # doesn't work
        #self.wr("\x1b[%s;%s;%s;%s$z" % (top + 1, left + 1, top + height, left + width))
        s = b" " * width
        bottom = top + height
        while top < bottom:
            self.goto(left, top)
            self.wr(s)
            top += 1

    def dialog_box(self, left, top, width, height, title=""):
        self.clear_box(left + 1, top + 1, width - 2, height - 2)
        self.draw_box(left, top, width, height)
        if title:
            #pos = (width - len(title)) / 2
            pos = 1
            self.goto(left + pos, top)
            self.wr(title)

    @classmethod
    def init_tty(cls):
        import tty, termios
        cls.org_termios = termios.tcgetattr(0)
        tty.setraw(0)

    @classmethod
    def deinit_tty(cls):
        import termios
        termios.tcsetattr(0, termios.TCSANOW, cls.org_termios)

    @classmethod
    def screen_size(cls):
        import select
        cls.wr(b"\x1b[18t")
        res = select.select([0], [], [], 0.2)[0]
        if not res:
            return (80, 24)
        resp = os.read(0, 32)
        assert resp.startswith(b"\x1b[8;") and resp[-1:] == b"t"
        vals = resp[:-1].split(b";")
        return (int(vals[2]), int(vals[1]))
