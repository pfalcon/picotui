from picotui.screen import *
from picotui.widgets import *
import dynapy.fem.lsdyna.keywords.control as c

if __name__ == "__main__":
    o = c.CONTROL_CONTACT()
    print(o.allcarditems)
    for ci in o.get_carditems().values():
        print(ci.name , ci.length)

    allcarditemslist = o.allcarditems.values()


    import functools

    def cmpci(s, o):
        if s.line == o.line:
            return s.pos < o.pos
        else:
            return s.line < o.line

    key = functools.cmp_to_key(cmpci)
    allcarditemslist = sorted(allcarditemslist, key=lambda c: (c.line, c.pos))
    print(allcarditemslist)

    s = Screen()
    try:
        s.init_tty()
        s.enable_mouse()
        s.attr_color(C_WHITE, C_BLUE)
        s.cls()
        s.attr_reset()
        d = Dialog(5, 5, 81, 4)

        x0 = 1
        y0 = 0

        # Can add a raw string to dialog, will be converted to WLabel
        kw = WLabel("%s" % (o.keyword))
        kw.attr_color(C_BLACK, C_RED)
        print(dir(kw))
        # print(kw.attr_color())
        d.add(1, 1, "%s" % o.keyword)
        for ci in allcarditemslist:
            d.add(ci.pos+x0, 2*ci.line+y0, WLabel("%s" % (ci.name)))
            testentry = WTextEntry(ci.length, "%s" % (ci.value))
            d.add(ci.pos+x0, 2*ci.line+y0+1, testentry)
            # testentry.attr_color(COLOR_BLACK, COLOR_RED)

        # d.add(1, 3, "Dropdown:")
        # d.add(11, 3, WDropDown(10, ["Red", "Green", "Yellow"]))
        #
        # d.add(1, 4, "Combo:")
        # d.add(11, 4, WComboBox(8, "fo", ["foo", "foobar", "bar"]))
        #
        # d.add(1, 5, "Auto complete:")
        # d.add(15, 5, WAutoComplete(8, "fo", ["foo", "foobar", "bar", "car", "dar"]))
        #
        # d.add(1, 8, "Multiline:")
        # d.add(1, 9, WMultiEntry(26, 3, ["Example", "Text"]))
        #
        # d.add(30, 1, WFrame(18, 6, "Frame"))
        # d.add(31, 2, WCheckbox("State"))
        # d.add(31, 3, WRadioButton(["Red", "Green", "Yellow"]))
        #
        # d.add(30, 8, "List:")
        # d.add(30, 9, WListBox(16, 4, ["choice%d" % i for i in range(10)]))

        b = WButton(8, "OK")
        d.add(10, 25, b)
        b.finish_dialog = ACTION_OK

        b = WButton(8, "Cancel")
        d.add(30, 25, b)
        b.finish_dialog = ACTION_CANCEL

        # d.redraw()
        res = d.loop()
    finally:
        s.goto(0, 50)
        s.cursor(True)
        s.disable_mouse()
        s.deinit_tty()

    print("Result:", res)