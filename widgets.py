from basewidget import *
from editorext import *


class Dialog(Widget):

    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.childs = []

    def add(self, x, y, widget):
        widget.set_xy(self.x + x, self.y + y)
        self.childs.append(widget)
        widget.owner = self

    def redraw(self):
        self.dialog_box(self.x, self.y, self.w, self.h)
        for w in self.childs:
            w.redraw()

    def find_focusable_by_idx(self, from_idx, direction):
        sz = len(self.childs)
        while 0 <= from_idx < sz:
            if self.childs[from_idx].focusable:
                return from_idx, self.childs[from_idx]
            from_idx = (from_idx + direction) % sz
        return None, None

    def find_focusable_by_xy(self, x, y):
        for w in self.childs:
            if w.focusable and w.inside(x, y):
                return w

    def loop(self):
        self.focus_idx, self.focus_w = self.find_focusable_by_idx(0, 1)
        if self.focus_w:
            self.focus_w.focus = True
        super().cursor(False)
        return super().loop()

    def change_focus(self, widget):
        if widget is self.focus_w:
            return
        if self.focus_w:
            self.focus_w.focus = False
            self.focus_w.redraw()
        self.focus_w = widget
        widget.focus = True
        widget.redraw()

    def move_focus(self, direction):
        prev_idx = (self.focus_idx + direction) % len(self.childs)
        self.focus_idx, new_w = self.find_focusable_by_idx(prev_idx, direction)
        self.change_focus(new_w)

    def handle_key(self, key):
        if key == KEY_QUIT:
            return key
        if key == KEY_TAB:
            self.move_focus(1)
        elif key == KEY_SHIFT_TAB:
            self.move_focus(-1)
        elif self.focus_w:
            res = self.focus_w.handle_key(key)
            if res == ACTION_PREV:
                self.move_focus(-1)
            elif res == ACTION_NEXT:
                self.move_focus(1)
            else:
                return res

    def handle_mouse(self, x, y):
        # Work in absolute coordinates
        if self.inside(x, y):
            w = self.find_focusable_by_xy(x, y)
#            print(w)
            if w:
                self.change_focus(w)
                return w.handle_mouse(x, y)


class WLabel(Widget):

    def __init__(self, text):
        self.t = text
        self.h = 1
        self.w = len(text)

    def redraw(self):
        self.goto(self.y, self.x)
        self.wr(self.t)


class WButton(Widget):

    focusable = True

    def __init__(self, text):
        self.t = text
        self.h = 1
        self.w = len(text) + 2
        self.disabled = False
        self.focus = False
        self.finish_dialog = False

    def redraw(self):
        self.goto(self.y, self.x)
        if self.disabled:
            self.attr_color(COLOR_WHITE, COLOR_GRAY)
        else:
            if self.focus:
                self.attr_color(COLOR_BRIGHT_WHITE, COLOR_GREEN)
            else:
                self.attr_color(COLOR_BLACK, COLOR_GREEN)
        self.wr(" " + self.t + " ")
        self.attr_reset()

    def handle_mouse(self, x, y):
        if not self.disabled:
            if self.finish_dialog:
                return self
            else:
                self.on_click()

    def on_click(self):
        pass


class WFrame(Widget):

    def __init__(self, w, h, title=""):
        self.w = w
        self.h = h
        self.t = title

    def redraw(self):
        self.draw_box(self.x, self.y, self.w, self.h)
        if self.t:
            pos = 1
            self.goto(self.y, self.x + pos)
            self.wr(" %s " % self.t)


class WCheckbox(Widget):

    focusable = True

    def __init__(self, title):
        self.t = title
        self.h = 1
        self.w = 4 + len(title)
        self.state = True

    def redraw(self):
        self.goto(self.y, self.x)
        self.wr("[x] " if self.state else "[ ] ")
        self.wr(self.t)

    def handle_mouse(self, x, y):
        self.state = not self.state
        self.redraw()


class WRadioButton(Widget):

    focusable = True

    def __init__(self, titles):
        self.titles = titles
        self.choice = 0
        self.h = len(titles)
        self.w = 4 + max((len(t) for t in titles))

    def redraw(self):
        i = 0
        for t in self.titles:
            self.goto(self.y + i, self.x)
            self.wr("(*) " if self.choice == i else "( ) ")
            self.wr(t)
            i += 1

    def handle_mouse(self, x, y):
        self.choice = y - self.y
        self.redraw()


class WListBox(EditorExt):

    focusable = True

    def __init__(self, w, h, items):
        EditorExt.__init__(self)
        self.items = items
        self.choice = 0
        self.width = w
        self.w = w
        self.height = h
        self.h = h
        self.set_lines(items)

    def set_xy(self, x, y):
        self.x = x
        self.y = y
        self.left = x
        self.top = y

    def show_line(self, l, i):
        hlite = self.cur_line == i
        if hlite:
            self.attr_color(COLOR_BRIGHT_WHITE, COLOR_GREEN)
        l = l[:self.width]
        self.wr(l)
        self.clear_num_pos(self.width - len(l))
        if hlite:
            self.attr_reset()

    def handle_mouse(self, x, y):
        super().handle_mouse(x, y)
        self.redraw()

    def handle_key(self, key):
        res = super().handle_key(key)
        self.redraw()
        return res

    def handle_edit_key(self, key):
        pass

    @staticmethod
    def cursor(onoff):
        pass


class WPopupList(Dialog):

    class OneShotList(WListBox):

        def handle_key(self, key):
            if key == KEY_ENTER:
                return ACTION_OK
            if key == KEY_ESC:
                return ACTION_CANCEL
            return super().handle_key(key)

        def handle_mouse(self, x, y):
            super().handle_mouse(x, y)
            # Mouse click finishes selection
            return ACTION_OK

    def __init__(self, x, y, w, h, items):
        super().__init__(x, y, w, h)
        self.list = self.OneShotList(w - 2, h - 2, items)
        self.add(1, 1, self.list)

    def handle_mouse(self, x, y):
        if not self.inside(x, y):
            return ACTION_CANCEL
        return super().handle_mouse(x, y)

    def get_choice(self):
        return self.list.cur_line


class WDropDown(Widget):

    focusable = True

    def __init__(self, w, items):
        self.items = items
        self.choice = 0
        self.h = 1
        self.w = w

    def redraw(self):
        self.goto(self.y, self.x)
        self.attr_color(COLOR_BLACK, COLOR_CYAN)
        self.wr_fixedw(self.items[self.choice], self.w - 2)
        self.wr(" v")
        self.attr_reset()

    def handle_mouse(self, x, y):
        popup = WPopupList(self.x, self.y + 1, self.w, 5, self.items)
        res = popup.loop()
        if res == ACTION_OK:
            self.choice = popup.get_choice()
        self.owner.redraw()
