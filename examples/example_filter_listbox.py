#
# This example shows how to change the items of a ListBox widget
# when the current selection of a DropDown widget changes.
#
from picotui.screen import Screen
from picotui.widgets import *
from picotui.defs import *


if __name__ == "__main__":

    s = Screen()

    # Set the list of all available DropDown choices
    choices = ["Green1", "Green2", "Green3", "Red1", "Red2", "Red3", "Yellow1", "Yellow2", "Yellow3"]

    try:
        s.init_tty()
        s.enable_mouse()
        s.attr_color(C_WHITE, C_BLUE)
        s.cls()
        s.attr_reset()
        d = Dialog(5, 5, 20, 12)

        # DropDown and ListBox widgets
        d.add(1, 1, "Dropdown:")
        w_dropdown = WDropDown(10, ["All", "Red", "Green", "Yellow"])
        d.add(11, 1, w_dropdown)

        d.add(1, 3, "List:")
        w_listbox = WListBox(16, 4, choices)
        d.add(1, 4, w_listbox)

        # Filter the ListBox based on the DropDown selection
        def dropdown_changed(w):
            new_choices = []
            for i in range(len(choices)):
                if w.items[w.choice] == "All" or w.items[w.choice] in choices[i]:
                    new_choices.append(choices[i])

            # As we're going to set completely new items, reset current/top item of the widget
            w_listbox.top_line = 0
            w_listbox.cur_line = 0
            w_listbox.row = 0
            w_listbox.set_items(new_choices)
        w_dropdown.on("changed", dropdown_changed)

        b = WButton(8, "OK")
        d.add(2, 10, b)
        b.finish_dialog = ACTION_OK

        b = WButton(8, "Cancel")
        d.add(12, 10, b)
        b.finish_dialog = ACTION_CANCEL

        res = d.loop()
    finally:
        s.goto(0, 50)
        s.cursor(True)
        s.disable_mouse()
        s.deinit_tty()

    print("Result:", res)
