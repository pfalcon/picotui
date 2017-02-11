from picotui.widgets import *
from picotui.menu import *
from picotui.context import Context


# Dialog on the screen
d = None

# This routine is called to redraw screen "in menu's background"
def screen_redraw(s, allow_cursor=False):
    s.attr_color(C_WHITE, C_BLUE)
    s.cls()
    s.attr_reset()
    d.redraw()


# We have two independent widgets on screen: dialog and main menu,
# so can't call their individual loops, and instead should have
# "main loop" to route events to currently active widget, and
# switch the active one based on special events.
def main_loop():
    while 1:
        key = m.get_input()

        if isinstance(key, list):
            # Mouse click
            x, y = key
            if m.inside(x, y):
                m.focus = True

        if m.focus:
            # If menu is focused, it gets events. If menu is cancelled,
            # it loses focus. Otherwise, if menu selection is made, we
            # quit with with menu result.
            res = m.handle_input(key)
            if res == ACTION_CANCEL:
                m.focus = False
            elif res is not None and res is not True:
                return res
        else:
            # If menu isn't focused, it can be focused by pressing F9.
            if key == KEY_F9:
                m.focus = True
                m.redraw()
                continue
            # Otherwise, dialog gets input
            res = d.handle_input(key)
            if res is not None and res is not True:
                return res


with Context():

    d = Dialog(10, 5, 40, 13)
    d.add(1, 1, WLabel("Label:"))
    d.add(1, 2, WListBox(16, 4, ["choice%d" % i for i in range(10)]))
    d.add(1, 7, WDropDown(10, ["Red", "Green", "Yellow"]))

    b = WButton(8, "OK")
    d.add(3, 10, b)
    b.finish_dialog = ACTION_OK

    b = WButton(8, "Cancel")
    d.add(20, 10, b)
    b.finish_dialog = ACTION_CANCEL

    screen_redraw(Screen)
    Screen.set_screen_redraw(screen_redraw)

    menu_file = WMenuBox([("Open...", "Open"), ("Save", "S"), ("Save as...", "Sa"), ("Exit", "ex")])
    menu_edit = WMenuBox([("Copy", "copy"), ("Paste", "paste")])
    m = WMenuBar([("File", menu_file), ("Edit", menu_edit), ("About", "About")])
    m.permanent = True
    m.redraw()

    res = main_loop()


print("Result:", res)
