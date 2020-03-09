import unittest
from picotui.widgets import WListBox
from picotui.defs import KEY_DOWN
from picotui.context import Context


class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age


class UserListBox(WListBox):
    def __init__(self, width, height, items):
        super().__init__(w=width, h=height, items=items)

    def render_line(self, user):
        return user.name


class WListBoxTest(unittest.TestCase):
    def test_handle_key_with_custom_type_of_items(self):
        with Context():
            users = [User('admin', 30), User('root', 27)]
            widget = UserListBox(width=5, height=5, items=users)
            self.assertIsNone(widget.handle_key(KEY_DOWN))
