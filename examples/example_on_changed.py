#
# This example shows usage of "changed" event handlers to propagate
# current state of widgets to other parts of an app (to other widgets
# in this case).
#
from picotui.context import Context
from picotui.screen import Screen
from picotui.widgets import *
from picotui.defs import *


with Context():
    Screen.attr_color(C_WHITE, C_BLUE)
    Screen.cls()
    Screen.attr_reset()

    d = Dialog(5, 5, 50, 12)

    # Few widgets

    w_checkbox = WCheckbox("State")
    d.add(1, 1, w_checkbox)

    w_radio = WRadioButton(["Left", "Right"])
    d.add(1, 2, w_radio)

    d.add(1, 4, "Dropdown:")
    w_dropdown = WDropDown(10, ["Red", "Green", "Yellow"])
    d.add(11, 4, w_dropdown)

    d.add(30, 1, "List:")
    w_listbox = WListBox(16, 4, ["choice%d" % i for i in range(10)])
    d.add(30, 2, w_listbox)

    # Now labels mirroring last selected value of widgets above

    d.add(1, 8, "Selected checkbox value:")
    w_checkbox_val = WLabel("", w=8)
    d.add(30, 8, w_checkbox_val)

    def checkbox_changed(w):
        w_checkbox_val.t = str(w.choice)
        w_checkbox_val.redraw()
    w_checkbox.on("changed", checkbox_changed)


    d.add(1, 9, "Selected radio value:")
    w_radio_val = WLabel("", w=8)
    d.add(30, 9, w_radio_val)

    def radio_changed(w):
        w_radio_val.t = w.items[w.choice]
        w_radio_val.redraw()
    w_radio.on("changed", radio_changed)


    d.add(1, 10, "Selected dropdown value:")
    w_dropdown_val = WLabel("", w=8)
    d.add(30, 10, w_dropdown_val)

    def dropdown_changed(w):
        val = w.items[w.choice]
        w_dropdown_val.t = val
        w_dropdown_val.redraw()
    w_dropdown.on("changed", dropdown_changed)


    d.add(1, 11, "Selected listbox value:")
    w_listbox_val = WLabel("", w=8)
    d.add(30, 11, w_listbox_val)

    def listbox_changed(w):
        val = w.items[w.choice]
        w_listbox_val.t = val
        w_listbox_val.redraw()
    w_listbox.on("changed", listbox_changed)


    b = WButton(8, "OK")
    d.add(10, 16, b)
    b.finish_dialog = ACTION_OK

    b = WButton(8, "Cancel")
    d.add(30, 16, b)
    b.finish_dialog = ACTION_CANCEL

    res = d.loop()


print("Result:", res)
