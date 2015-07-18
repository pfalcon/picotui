import os


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
    def cls():
        Screen.wr(b"\x1b[2J")

    @staticmethod
    def goto(row, col):
        # TODO: When Python is 3.5, update this to use bytes
        Screen.wr("\x1b[%d;%dH" % (row + 1, col + 1))

    @staticmethod
    def clear_to_eol():
        Screen.wr(b"\x1b[0K")

    # Clear specified number of positions
    @staticmethod
    def clear_num_pos(num):
        if num > 0:
            Screen.wr("\x1b[%dX" % num)

    @staticmethod
    def cursor(onoff):
        if onoff:
            Screen.wr(b"\x1b[?25h")
        else:
            Screen.wr(b"\x1b[?25l")

    @classmethod
    def init_tty(cls):
        import tty, termios
        cls.org_termios = termios.tcgetattr(0)
        tty.setraw(0)

    @classmethod
    def deinit_tty(cls):
        import termios
        termios.tcsetattr(0, termios.TCSANOW, cls.org_termios)
