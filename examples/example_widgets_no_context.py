#
# This example is a variant of top-level example_widgets.py which
# doesn't use picotui.context.Context, but initializes and
# deinitializes screen "manually". Here only for completeness, use
# Context whenever possible.
#
from picotui.screen import Screen
from picotui.widgets import *
from picotui.defs import *


if __name__ == "__main__":

    s = Screen()
    try:
        s.init_tty()
        s.enable_mouse()
        s.attr_color(C_WHITE, C_BLUE)
        s.cls()
        s.attr_reset()
        d = Dialog(5, 5, 50, 12)

        # Can add a raw string to dialog, will be converted to WLabel
        d.add(1, 1, "Label:")
        d.add(11, 1, WLabel("it's me!"))

        d.add(1, 2, "Entry:")
        d.add(11, 2, WTextEntry(4, "foo"))

        d.add(1, 3, "Dropdown:")
        d.add(11, 3, WDropDown(10, ["Red", "Green", "Yellow"]))

        d.add(1, 4, "Combo:")
        d.add(11, 4, WComboBox(8, "fo", ["foo", "foobar", "bar"]))

        d.add(1, 5, "Auto complete:")
        d.add(15, 5, WAutoComplete(8, "fo", ["foo", "foobar", "bar", "car", "dar"]))

        d.add(1, 8, "Multiline:")
        d.add(1, 9, WMultiEntry(26, 3, ["Example", "Text"]))

        d.add(30, 1, WFrame(18, 6, "Frame"))
        d.add(31, 2, WCheckbox("State"))
        d.add(31, 3, WRadioButton(["Red", "Green", "Yellow"]))

        d.add(30, 8, "List:")
        d.add(30, 9, WListBox(16, 4, ["choice%d" % i for i in range(10)]))

        d.add(1, 13, "Button:")
        b = WButton(9, "Kaboom!")
        d.add(10, 13, b)
        b.on("click", lambda w: 1/0)

        d.add(1, 15, "Dialog buttons:")
        b = WButton(8, "OK")
        d.add(10, 16, b)
        # Instead of having on_click handler, buttons can finish a dialog
        # with a given result.
        b.finish_dialog = ACTION_OK

        b = WButton(8, "Cancel")
        d.add(30, 16, b)
        b.finish_dialog = ACTION_CANCEL

        #d.redraw()
        res = d.loop()
    finally:
        s.goto(0, 50)
        s.cursor(True)
        s.disable_mouse()
        s.deinit_tty()

    print("Result:", res)
