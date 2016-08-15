from .basewidget import *
from .editorext import *
from . import symbols


class Dialog(Widget):

    finish_on_esc = True

    def __init__(self, x, y, w=0, h=0, title=""):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = ""
        if title:
            self.title = " %s " % title
        self.childs = []
        # On both sides
        self.border_w = 2
        self.border_h = 2

    def add(self, x, y, widget):
        widget.set_xy(self.x + x, self.y + y)
        self.childs.append(widget)
        widget.owner = self

    def autosize(self):
        w = 0
        h = 0
        for wid in self.childs:
            w = max(w, wid.x - self.x + wid.w)
            h = max(h, wid.y - self.y + wid.h)
        self.w = max(self.w, w + self.border_w - 1)
        self.h = max(self.h, h + self.border_h - 1)

    def redraw(self):
        # Redraw widgets with cursor off
        self.cursor(False)
        self.dialog_box(self.x, self.y, self.w, self.h, self.title)
        for w in self.childs:
            w.redraw()
        # Then give widget in focus a chance to enable cursor
        if self.focus_w:
            self.focus_w.set_cursor()

    def find_focusable_by_idx(self, from_idx, direction):
        sz = len(self.childs)
        while 0 <= from_idx < sz:
            if self.childs[from_idx].focusable:
                return from_idx, self.childs[from_idx]
            from_idx = (from_idx + direction) % sz
        return None, None

    def find_focusable_by_xy(self, x, y):
        i = 0
        for w in self.childs:
            if w.focusable and w.inside(x, y):
                return i, w
            i += 1
        return None, None

    def loop(self):
        self.autosize()
        self.focus_idx, self.focus_w = self.find_focusable_by_idx(0, 1)
        if self.focus_w:
            self.focus_w.focus = True
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
        widget.set_cursor()

    def move_focus(self, direction):
        prev_idx = (self.focus_idx + direction) % len(self.childs)
        self.focus_idx, new_w = self.find_focusable_by_idx(prev_idx, direction)
        self.change_focus(new_w)

    def handle_key(self, key):
        if key == KEY_QUIT:
            return key
        if key == KEY_ESC and self.finish_on_esc:
            return ACTION_CANCEL
        if key == KEY_TAB:
            self.move_focus(1)
        elif key == KEY_SHIFT_TAB:
            self.move_focus(-1)
        elif self.focus_w:
            if key == KEY_ENTER:
                if self.focus_w.finish_dialog is not False:
                    return self.focus_w.finish_dialog
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
            self.focus_idx, w = self.find_focusable_by_xy(x, y)
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
        self.goto(self.x, self.y)
        self.wr(self.t)


class WButton(Widget):

    focusable = True

    def __init__(self, w, text):
        self.t = text
        self.h = 1
        self.w = w or len(text) + 2
        self.disabled = False
        self.focus = False
        self.finish_dialog = False

    def redraw(self):
        self.goto(self.x, self.y)
        if self.disabled:
            self.attr_color(COLOR_WHITE, COLOR_GRAY)
        else:
            if self.focus:
                self.attr_color(COLOR_BRIGHT_WHITE, COLOR_GREEN)
            else:
                self.attr_color(COLOR_BLACK, COLOR_GREEN)
        self.wr(self.t.center(self.w))
        self.attr_reset()

    def handle_mouse(self, x, y):
        if not self.disabled:
            if self.finish_dialog:
                return self
            else:
                self.on_click()

    def handle_key(self, key):
        if key == KEY_UP:
            return ACTION_PREV
        if key == KEY_DOWN:
            return ACTION_NEXT

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
            self.goto(self.x + pos, self.y)
            self.wr(" %s " % self.t)


class WCheckbox(Widget):

    focusable = True

    def __init__(self, title, state=False):
        super().__init__()
        self.t = title
        self.h = 1
        self.w = 4 + len(title)
        self.state = state
        self.focus = False

    def redraw(self):
        self.goto(self.x, self.y)
        if self.focus:
            self.attr_color(COLOR_BRIGHT_BLUE, None)
        self.wr("[x] " if self.state else "[ ] ")
        self.wr(self.t)
        self.attr_reset()

    def flip(self):
        self.state = not self.state
        self.redraw()
        self.signal("changed")

    def handle_mouse(self, x, y):
        self.flip()

    def handle_key(self, key):
        if key == KEY_UP:
            return ACTION_PREV
        if key == KEY_DOWN:
            return ACTION_NEXT
        if key == b" ":
            self.flip()


class WRadioButton(Widget):

    focusable = True

    def __init__(self, titles):
        self.titles = titles
        self.choice = 0
        self.h = len(titles)
        self.w = 4 + self.longest(titles)
        self.focus = False

    def redraw(self):
        i = 0
        if self.focus:
            self.attr_color(COLOR_BRIGHT_BLUE, None)
        for t in self.titles:
            self.goto(self.x, self.y + i)
            self.wr("(*) " if self.choice == i else "( ) ")
            self.wr(t)
            i += 1
        self.attr_reset()

    def handle_mouse(self, x, y):
        self.choice = y - self.y
        self.redraw()

    def handle_key(self, key):
        if key == KEY_UP:
            return ACTION_PREV
        if key == KEY_DOWN:
            return ACTION_NEXT


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
        self.focus = False

    def render_line(self, l):
        # Default identity implementation is suitable for
        # items being list of strings.
        return l

    def show_line(self, l, i):
        hlite = self.cur_line == i
        if hlite:
            if self.focus:
                self.attr_color(COLOR_BRIGHT_WHITE, COLOR_GREEN)
            else:
                self.attr_color(COLOR_BLACK, COLOR_GREEN)
        l = self.render_line(l)[:self.width]
        self.wr(l)
        self.clear_num_pos(self.width - len(l))
        if hlite:
            self.attr_reset()

    def handle_mouse(self, x, y):
        res = super().handle_mouse(x, y)
        self.redraw()
        return res

    def handle_key(self, key):
        res = super().handle_key(key)
        self.redraw()
        return res

    def handle_edit_key(self, key):
        pass

    def set_cursor(self):
        Widget.set_cursor(self)

    def cursor(self, state):
        # Force off
        super().cursor(False)


class WPopupList(Dialog):

    class OneShotList(WListBox):

        def handle_key(self, key):
            if key == KEY_ENTER:
                return ACTION_OK
            if key == KEY_ESC:
                return ACTION_CANCEL
            return super().handle_key(key)

        def handle_mouse(self, x, y):
            if super().handle_mouse(x, y) == True:
                # (Processed) mouse click finishes selection
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

    def get_selected_value(self):
        if not self.list.content:
            return None
        return self.list.content[self.list.cur_line]


class WDropDown(Widget):

    focusable = True

    def __init__(self, w, items):
        self.items = items
        self.choice = 0
        self.h = 1
        self.w = w
        self.focus = False

    def redraw(self):
        self.goto(self.x, self.y)
        if self.focus:
            self.attr_color(COLOR_BRIGHT_WHITE, COLOR_CYAN)
        else:
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

    def handle_key(self, key):
        self.handle_mouse(0, 0)


class WTextEntry(EditorExt):

    focusable = True

    def __init__(self, w, text):
        super().__init__(width=w, height=1)
        self.t = text
        self.h = 1
        self.w = w
        self.focus = False
        self.set_lines([text])
        self.col = len(text)
        self.adjust_cursor_eol()
        self.just_started = True

    def get_text(self):
        return self.get_cur_line()

    def handle_cursor_keys(self, key):
        if super().handle_cursor_keys(key):
            if self.just_started:
                self.just_started = False
                self.redraw()
            return True
        return False

    def handle_edit_key(self, key):
        if key == KEY_ENTER:
            # Don't treat as editing key
            return True
        if self.just_started:
            if key != KEY_BACKSPACE:
                # Overwrite initial string with new content
                self.set_lines([""])
                self.col = 0
            self.just_started = False

        return super().handle_edit_key(key)

    def handle_mouse(self, x, y):
        if self.just_started:
            self.just_started = False
            self.redraw()
        super().handle_mouse(x, y)

    def show_line(self, l, i):
        if self.just_started:
            fg = COLOR_WHITE
        else:
            fg = COLOR_BLACK
        self.attr_color(fg, COLOR_CYAN)
        super().show_line(l, i)
        self.attr_reset()


class WComboBox(WTextEntry):

    popup_class = WPopupList
    popup_h = 5

    def __init__(self, w, text, items):
        # w - 1 width goes to Editor widget
        super().__init__(w - 1, text)
        # We have full requested width, will show arrow symbol as last char
        self.w = w
        self.items = items

    def redraw(self):
        self.goto(self.x + self.w - 1, self.y)
        self.wr(symbols.DOWN_ARROW)
        super().redraw()

    def get_choices(self, substr):
        return self.items

    def show_popup(self):
        choices = self.get_choices(self.get_text())
        popup = self.popup_class(self.x, self.y + 1, self.longest(choices) + 2, self.popup_h, choices)
        popup.main_widget = self
        res = popup.loop()
        if res == ACTION_OK:
            val = popup.get_selected_value()
            if val is not None:
                self.set_lines([val])
                self.col = sys.maxsize
                self.adjust_cursor_eol()
                self.just_started = False
        self.owner.redraw()

    def handle_key(self, key):
        if key == KEY_DOWN:
            self.show_popup()
        else:
            return super().handle_key(key)

    def handle_mouse(self, x, y):
        if x == self.x + self.w - 1:
            self.show_popup()
        else:
            super().handle_mouse(x, y)


class WCompletionList(WPopupList):

    def __init__(self, x, y, w, h, items):
        Dialog.__init__(self, x, y, w, h)
        self.list = self.OneShotList(w - 2, h - 2, items)
        self.add(1, 1, self.list)
        chk = WCheckbox("Prefix")
        def is_prefix_changed(wid):
            main = self.main_widget
            choices = main.get_choices(main.get_text(), wid.state)
            self.list.set_lines(choices)
            self.list.top_line = 0
            self.list.cur_line = 0
            self.list.row = 0
            self.list.redraw()
        chk.on("changed", is_prefix_changed)
        self.add(1, h - 1, chk)


class WAutoComplete(WComboBox):

    popup_class = WCompletionList

    def get_choices(self, substr, only_prefix=False):
        substr = substr.lower()
        if only_prefix:
            choices = list(filter(lambda x: x.lower().startswith(substr), self.items))
        else:
            choices = list(filter(lambda x: substr in x.lower(), self.items))
        return choices
