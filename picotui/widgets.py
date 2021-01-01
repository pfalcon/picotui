from .basewidget import *
from .editorext import *
from .defs import *


__all__ = (
    "ACTION_OK",
    "ACTION_CANCEL",
    "ACTION_NEXT",
    "ACTION_PREV",
    "EditableWidget",
    "Dialog",
    "WLabel",
    "WFrame",
    "WButton",
    "WCheckbox",
    "WRadioButton",
    "WListBox",
    "WPopupList",
    "WDropDown",
    "WTextEntry",
    "WMultiEntry",
    "WComboBox",
    "WCompletionList",
    "WAutoComplete",
)

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
        self.focus_w = None
        self.focus_idx = -1

    def add(self, x, y, widget):
        if isinstance(widget, str):
            # Convert raw string to WLabel
            widget = WLabel(widget)
        widget.set_xy(self.x + x, self.y + y)
        self.childs.append(widget)
        widget.owner = self

    def autosize(self, extra_w=0, extra_h=0):
        w = 0
        h = 0
        for wid in self.childs:
            w = max(w, wid.x - self.x + wid.w)
            h = max(h, wid.y - self.y + wid.h)
        self.w = max(self.w, w + self.border_w - 1) + extra_w
        self.h = max(self.h, h + self.border_h - 1) + extra_h

    def redraw(self):
        # Init some state on first redraw
        if self.focus_idx == -1:
            self.autosize()
            self.focus_idx, self.focus_w = self.find_focusable_by_idx(0, 1)
            if self.focus_w:
                self.focus_w.focus = True

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
            if isinstance(self.childs[from_idx], FocusableWidget):
                return from_idx, self.childs[from_idx]
            from_idx = (from_idx + direction) % sz
        return None, None

    def find_focusable_by_xy(self, x, y):
        i = 0
        for w in self.childs:
            if isinstance(w, FocusableWidget) and w.inside(x, y):
                return i, w
            i += 1
        return None, None

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

    def __init__(self, text, w=0):
        self.t = text
        self.h = 1
        self.w = w
        if not w:
            self.w = len(text)

    def redraw(self):
        self.goto(self.x, self.y)
        self.wr_fixedw(self.t, self.w)


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


class WButton(FocusableWidget):

    def __init__(self, w, text):
        Widget.__init__(self)
        self.t = text
        self.h = 1
        self.w = w or len(text) + 2
        self.disabled = False
        self.focus = False
        self.finish_dialog = False

    def redraw(self):
        self.goto(self.x, self.y)
        if self.disabled:
            self.attr_color(C_WHITE, C_GRAY)
        else:
            if self.focus:
                self.attr_color(C_B_WHITE, C_GREEN)
            else:
                self.attr_color(C_BLACK, C_GREEN)
        self.wr(self.t.center(self.w))
        self.attr_reset()

    def handle_mouse(self, x, y):
        if not self.disabled:
            if self.finish_dialog is not False:
                return self.finish_dialog
            else:
                self.signal("click")

    def handle_key(self, key):
        if key == KEY_UP or key == KEY_LEFT:
            return ACTION_PREV
        if key == KEY_DOWN or key == KEY_RIGHT:
            return ACTION_NEXT
        # For dialog buttons (.finish_dialog=True), KEY_ENTER won't
        # reach here.
        if key == KEY_ENTER:
            self.signal("click")

    def on_click(self):
        pass


class WCheckbox(ChoiceWidget):

    def __init__(self, title, choice=False):
        super().__init__(choice)
        self.t = title
        self.h = 1
        self.w = 4 + len(title)
        self.focus = False

    def redraw(self):
        self.goto(self.x, self.y)
        if self.focus:
            self.attr_color(C_B_BLUE, None)
        self.wr("[x] " if self.choice else "[ ] ")
        self.wr(self.t)
        self.attr_reset()

    def flip(self):
        self.choice = not self.choice
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


class WRadioButton(ItemSelWidget):

    def __init__(self, items):
        super().__init__(items)
        self.h = len(items)
        self.w = 4 + self.longest(items)
        self.focus = False

    def redraw(self):
        i = 0
        if self.focus:
            self.attr_color(C_B_BLUE, None)
        for t in self.items:
            self.goto(self.x, self.y + i)
            self.wr("(*) " if self.choice == i else "( ) ")
            self.wr(t)
            i += 1
        self.attr_reset()

    def handle_mouse(self, x, y):
        self.choice = y - self.y
        self.redraw()
        self.signal("changed")

    def handle_key(self, key):
        if key == KEY_UP:
            self.move_sel(-1)
        elif key == KEY_DOWN:
            self.move_sel(1)


class WListBox(EditorExt, ChoiceWidget):

    def __init__(self, w, h, items):
        EditorExt.__init__(self)
        ChoiceWidget.__init__(self, 0)
        self.width = w
        self.w = w
        self.height = h
        self.h = h
        self.set_items(items)
        self.focus = False

    def set_items(self, items):
        self.items = items
        self.set_lines(items)

    def render_line(self, l):
        # Default identity implementation is suitable for
        # items being list of strings.
        return l

    def show_line(self, l, i):
        hlite = self.cur_line == i
        if hlite:
            if self.focus:
                self.attr_color(C_B_WHITE, C_GREEN)
            else:
                self.attr_color(C_BLACK, C_GREEN)
        if i != -1:
            l = self.render_line(l)[:self.width]
            self.wr(l)
        self.clear_num_pos(self.width - len(l))
        if hlite:
            self.attr_reset()

    def handle_mouse(self, x, y):
        res = super().handle_mouse(x, y)
        self.choice = self.cur_line
        self.redraw()
        self.signal("changed")
        return res

    def handle_key(self, key):
        res = super().handle_key(key)
        self.choice = self.cur_line
        self.redraw()
        self.signal("changed")
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

    def __init__(self, x, y, w, h, items, sel_item=0):
        super().__init__(x, y, w, h)
        self.list = self.OneShotList(w - 2, h - 2, items)
        self.list.cur_line = sel_item
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


class WDropDown(ChoiceWidget):

    def __init__(self, w, items, *, dropdown_h=5):
        super().__init__(0)
        self.items = items
        self.h = 1
        self.w = w
        self.dropdown_h = dropdown_h
        self.focus = False

    def redraw(self):
        self.goto(self.x, self.y)
        if self.focus:
            self.attr_color(C_B_WHITE, C_CYAN)
        else:
            self.attr_color(C_BLACK, C_CYAN)
        self.wr_fixedw(self.items[self.choice], self.w - 1)
        self.attr_reset()
        self.wr(DOWN_ARROW)

    def handle_mouse(self, x, y):
        popup = WPopupList(self.x, self.y + 1, self.w, self.dropdown_h, self.items, self.choice)
        res = popup.loop()
        if res == ACTION_OK:
            self.choice = popup.get_choice()
            self.signal("changed")
        self.owner.redraw()

    def handle_key(self, key):
        self.handle_mouse(0, 0)


class WTextEntry(EditorExt, EditableWidget):

    def __init__(self, w, text):
        EditorExt.__init__(self, width=w, height=1)
        self.t = text
        self.h = 1
        self.w = w
        self.focus = False
        self.set(text)
        self.col = len(text)
        self.adjust_cursor_eol()
        self.just_started = True

    def get(self):
        return self.get_cur_line()

    def set(self, text):
        self.set_lines([text])

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
            fg = C_WHITE
        else:
            fg = C_BLACK
        self.attr_color(fg, C_CYAN)
        super().show_line(l, i)
        self.attr_reset()


class WMultiEntry(EditorExt, EditableWidget):

    def __init__(self, w, h, lines):
        EditorExt.__init__(self, width=w, height=h)
        self.h = h
        self.w = w
        self.focus = False
        self.set_lines(lines)

    def get(self):
        return self.content

    def set(self, lines):
        self.set_lines(lines)

    def show_line(self, l, i):
        self.attr_color(C_BLACK, C_CYAN)
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
        self.wr(DOWN_ARROW)
        super().redraw()

    def get_choices(self, substr):
        return self.items

    def show_popup(self):
        choices = self.get_choices(self.get())
        popup = self.popup_class(self.x, self.y + 1, self.longest(choices) + 2, self.popup_h, choices)
        popup.main_widget = self
        res = popup.loop()
        if res == ACTION_OK:
            val = popup.get_selected_value()
            if val is not None:
                self.set_lines([val])
                self.margin = 0
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
            choices = main.get_choices(main.get(), wid.choice)
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
