import os
import signal


class Screen:

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
    def attr_color(fg, bg=-1):
        if bg == -1:
            bg = fg >> 4
            fg &= 0xf
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
                Screen.wr("\x1b[0;%d;%dm" % (fg + 30, bg + 40))

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
    def enable_mouse(cls):
        # Mouse reporting - X10 compatibility mode
        cls.wr(b"\x1b[?1000h")

    @classmethod
    def disable_mouse(cls):
        # Mouse reporting - X10 compatibility mode
        cls.wr(b"\x1b[?1000l")

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

    # Set function to redraw an entire (client) screen
    # This is called to restore original screen, as we don't save it.
    @classmethod
    def set_screen_redraw(cls, handler):
        cls.screen_redraw = handler

    @classmethod
    def set_screen_resize(cls, handler):
        signal.signal(signal.SIGWINCH, lambda sig, stk: handler(cls))
