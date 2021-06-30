import unittest

from group_when_any import group_when_any


class TestGroupWhenAny(unittest.TestCase):
    def test_group_when_any(self):
        values = [1, 2, 3]
        condition = lambda a, b: abs(a - b) == 1
        groups = group_when_any(values, condition)
        self.assertEquals(groups, [[1, 2, 3]])
