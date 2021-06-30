import unittest
import numpy as np

from detect_objects import detect_objects, are_areas_neighbouring, intersects_on_x_axis, intersects_on_y_axis


class TestDetectObjects(unittest.TestCase):
    def test_detect_objects_with_one_pixel(self):
        image = np.array((
            (255,),
        ))
        areas = detect_objects(image)
        self.assertEquals(areas, [[0, 0, 0, 0]])

    def test_detect_objects_with_two_pixels(self):
        image = np.array((
            (255, 255),
        ))
        areas = detect_objects(image)
        self.assertEquals(areas, [[0, 0, 1, 0]])

    def test_detect_objects_with_blank_space(self):
        image = np.array((
            (0,),
            (255,),
        ))
        areas = detect_objects(image)
        self.assertEquals(areas, [[0, 1, 0, 1]])

    def test_detect_objects_with_diagonal_edge(self):
        image = np.array((
            (0, 255),
            (255, 255),
        ))
        areas = detect_objects(image)
        self.assertEquals(areas, [[0, 0, 1, 1]])


class TestAreAreasNeighbouring(unittest.TestCase):
    def test_neighbouring_on_the_left_and_the_right(self):
        a = [0, 0, 1, 1]
        b = [2, 0, 3, 0]
        self.assertTrue(are_areas_neighbouring(a, b))

    def test_neighbouring_diagonal(self):
        a = [0, 0, 1, 1]
        b = [2, 2, 3, 3]
        self.assertTrue(are_areas_neighbouring(a, b))

    def test_neighbouring_diagonal_2(self):
        a = [2, 2, 3, 3]
        b = [0, 0, 1, 1]
        self.assertTrue(are_areas_neighbouring(a, b))

    def test_neighbouring_on_the_left_and_the_right_apart(self):
        a = [0, 0, 1, 1]
        b = [2, 3, 3, 4]
        self.assertFalse(are_areas_neighbouring(a, b))

    def test_neighbouring_on_the_right_and_the_left(self):
        a = [2, 0, 3, 1]
        b = [0, 0, 1, 1]
        self.assertTrue(are_areas_neighbouring(a, b))

    def test_neighbouring_on_the_right_and_the_left_apart(self):
        a = [2, 4, 3, 4]
        b = [0, 0, 1, 1]
        self.assertFalse(are_areas_neighbouring(a, b))

    def test_neighbouring_on_the_top_and_the_bottom(self):
        a = [0, 0, 1, 1]
        b = [0, 2, 1, 3]
        self.assertTrue(are_areas_neighbouring(a, b))

    def test_neighbouring_on_the_top_and_the_bottom_apart(self):
        a = [0, 0, 1, 1]
        b = [3, 2, 4, 3]
        self.assertFalse(are_areas_neighbouring(a, b))

    def test_neighbouring_on_the_bottom_and_the_top(self):
        a = [0, 2, 1, 3]
        b = [0, 0, 1, 1]
        self.assertTrue(are_areas_neighbouring(a, b))

    def test_neighbouring_on_the_bottom_and_the_top_apart(self):
        a = [3, 2, 4, 3]
        b = [0, 0, 1, 1]
        self.assertFalse(are_areas_neighbouring(a, b))

    def test_neighbouring_apart(self):
        a = [0, 1, 0, 1]
        b = [3, 1, 12, 1]
        self.assertFalse(are_areas_neighbouring(a, b))

    def test_neighbouring_one_covers_x_range_of_other(self):
        a = [291, 392, 332, 401]
        b = [289, 402, 334, 413]
        self.assertTrue(are_areas_neighbouring(a, b))

    def test_top_bottom_overlapping(self):
        a = [0, 0, 1, 1]
        b = [0, 1, 1, 2]
        self.assertTrue(are_areas_neighbouring(a, b))


class TestIntersectsOnXAxis(unittest.TestCase):
    def test_same_width(self):
        a = [0, 0, 1, 0]
        b = [0, 1, 1, 1]
        self.assertTrue(intersects_on_x_axis(a, b))


class TestIntersectsOnYAxis(unittest.TestCase):
    def test_one_covers_range_of_other(self):
        a = [0, 1, 0, 2]
        b = [0, 0, 0, 3]
        self.assertTrue(intersects_on_y_axis(a, b))
