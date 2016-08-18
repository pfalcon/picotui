from picotui.screen import *
from picotui.widgets import *


if __name__ == "__main__":

    s = Screen()
    try:
        s.init_tty()
        s.enable_mouse()
        s.attr_color(COLOR_WHITE, COLOR_BLUE)
        s.cls()
        s.attr_reset()
        d = Dialog(10, 5, 40, 13)
        d.add(1, 1, WLabel("Label:"))
#        d.add(8, 1, WTextEntry(4, "foo"))
#        d.add(8, 1, WComboBox(4, "fo", ["foo", "foobar", "bar"]))
        d.add(8, 1, WAutoComplete(8, "fo", ["foo", "foobar", "bar", "car", "dar"]))
        d.add(1, 2, WListBox(16, 4, ["choice%d" % i for i in range(10)]))
        d.add(1, 7, WDropDown(10, ["Red", "Green", "Yellow"]))

        d.add(20, 1, WFrame(18, 6, "Choices"))
        d.add(21, 2, WCheckbox("State"))
        d.add(21, 3, WRadioButton(["Red", "Green", "Yellow"]))

        # Can add a raw string to dialog, will be converted to WLabel
        d.add(1, 9, "Multiline:")
        d.add(1, 10, WMultiEntry(30, 3, ["Example", "Text"]))

        b = WButton(8, "OK")
        d.add(7, 14, b)
        b.finish_dialog = True

        b = WButton(8, "Cancel")
        d.add(24, 14, b)
        b.finish_dialog = True

        #d.redraw()
        res = d.loop()
    finally:
        s.goto(0, 50)
        s.cursor(True)
        s.deinit_tty()

    print("Result:", res)
