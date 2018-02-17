from .screen import Screen


class Context:

    def __init__(self, cls=True, mouse=True):
        self.cls = cls
        self.mouse = mouse

    def __enter__(self):
        Screen.init_tty()
        if self.mouse:
            Screen.enable_mouse()
        if self.cls:
            Screen.cls()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mouse:
            Screen.disable_mouse()
        Screen.goto(0, 50)
        Screen.cursor(True)
        Screen.deinit_tty()
        # This makes sure that entire screenful is scrolled up, and
        # any further output happens on a normal terminal line.
        print()
