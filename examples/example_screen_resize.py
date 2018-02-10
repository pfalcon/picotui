from picotui.widgets import *
from picotui.menu import *
from picotui.context import Context


# Dialog on the screen
d = None


# This routine is called on screen resize
def screen_resize(s):
    global d
    # Widgets in dialog store absolute screen coordinates, so
    # we need to recreate it from scratch for new dimensions.
    d = create_dialog()
    screen_redraw(s)


# This routine is called to redraw screen
def screen_redraw(s, allow_cursor=False):
    global d
    s.attr_color(C_WHITE, C_BLUE)
    s.cls()
    s.attr_reset()
    d.redraw()


def create_dialog():
    width, height = Screen.screen_size()

    d = Dialog((width - 40) // 2, (height - 13) // 2, 40, 13)
    d.add(1, 1, WLabel("Label:"))
    d.add(1, 2, WListBox(16, 4, ["choice%d" % i for i in range(10)]))
    d.add(1, 7, WDropDown(10, ["Red", "Green", "Yellow"]))

    b = WButton(8, "OK")
    d.add(3, 10, b)
    b.finish_dialog = ACTION_OK

    b = WButton(8, "Cancel")
    d.add(20, 10, b)
    b.finish_dialog = ACTION_CANCEL

    return d


with Context():
    d = create_dialog()

    screen_redraw(Screen)
    Screen.set_screen_redraw(screen_redraw)
    Screen.set_screen_resize(screen_resize)

    res = d.loop()


print("Result:", res)
