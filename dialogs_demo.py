from picotui.context import Context
from picotui.dialogs import *


with Context():
    # Feel free to comment out extra dialogs to play with a particular
    # in detail
    d = DTextEntry(25, "Hello World", title="Wazzup?")
    res = d.result()
    d = DMultiEntry(25, 5, "Hello\nWorld".split("\n"), title="Comment:")
    res = d.result()


print(res)
