from picotui.screen import *
from picotui.widgets import *


if __name__ == "__main__":

    s = Screen()
    try:
        s.init_tty()
        s.enable_mouse()
        s.attr_color(C_WHITE, C_BLUE)
        s.cls()
        s.attr_reset()
        d = Dialog(5, 5, 50, 12, fcolor=C_RED, bcolor=C_WHITE)

        # Can add a raw string to dialog, will be converted to WLabel
        d.add(1, 1, "Label:")
        d.add(11, 1, WLabel("it's me!", fcolor=C_BLACK, bcolor=C_YELLOW))

        d.add(1, 2, "Entry:")
        d.add(11, 2, WTextEntry(4, "foo", fcolor=C_RED, bcolor=C_BLUE))

        d.add(1, 3, "Dropdown:")
        d.add(11, 3, WDropDown(10, ["Red", "Green", "Yellow"], scolor=C_RED, afcolor=C_YELLOW, abcolor=C_BLUE))
        
        d.add(1, 4, "Combo:")
        d.add(11, 4, WComboBox(8, "fo", ["foo", "foobar", "bar"], afcolor=C_YELLOW, abcolor=C_RED))

        d.add(1, 5, "Auto complete:")
        d.add(15, 5, WAutoComplete(8, "fo", ["foo", "foobar", "bar", "car", "dar"]))

        d.add(1, 8, "Multiline:")
        d.add(1, 9, WMultiEntry(26, 3, ["Example", "Text"], fcolor=C_BLUE, bcolor=C_GREEN))

        d.add(30, 1, WFrame(18, 6, "Frame", fcolor=C_BLUE, bcolor=C_RED))
        d.add(31, 2, WCheckbox("State", fcolor=C_GREEN, bcolor=C_RED, ffcolor=C_BLUE, fbcolor=C_YELLOW))
        d.add(31, 3, WRadioButton(["Red", "Green", "Yellow"], fcolor=C_RED, bcolor=C_YELLOW, ffcolor=C_BLUE, fbcolor=C_YELLOW))

        d.add(30, 8, "List:")
        d.add(30, 9, WListBox(16, 4, ["choice%d" % i for i in range(10)], fcolor=C_YELLOW, bcolor=C_BLUE, scolor=C_MAGENTA))

        d.add(1, 13, "Button:")
        b = WButton(9, "Kaboom!", fcolor=C_GREEN, bcolor=C_MAGENTA, ffcolor=C_BLACK, fbcolor=C_MAGENTA)
        d.add(10, 13, b)
        # You should actually subclass WButton and override method
        b.on("click", lambda w: 1/0)

        d.add(1, 15, "Dialog buttons:")
        b = WButton(8, "OK", fcolor=C_GREEN, bcolor=C_MAGENTA, ffcolor=C_BLACK, fbcolor=C_MAGENTA)
        d.add(10, 16, b)
        # Instead of having on_click handler, buttons can finish a dialog
        # with a given result.
        b.finish_dialog = ACTION_OK

        b = WButton(8, "Cancel", fcolor=C_GREEN, bcolor=C_MAGENTA, ffcolor=C_BLACK, fbcolor=C_MAGENTA)
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
