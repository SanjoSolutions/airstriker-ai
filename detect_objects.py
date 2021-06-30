import cv2 as cv

from group_when_any import group_when_any


def detect_objects(image):
    """
    :param image: Grayscale image.
    :return: Areas of objects.
    """
    image = image > 0
    areas = []
    for y in range(image.shape[0]):
        previous = None
        x_to_area = dict()
        for x in range(image.shape[1]):
            if image[y, x]:
                if x in x_to_area:
                    area = x_to_area[x]
                elif (
                    previous and
                    x - previous[0] <= 1 and
                    y - previous[1] <= 1
                ):
                    area = areas[-1]
                else:
                    area = None
                if area:
                    area[2] = x
                    area[3] = y
                    x_to_area[x] = area
                else:
                    area = [x, y, x, y]
                    areas.append(area)
                    x_to_area[x] = area
                previous = (x, y)
    areas = group_neighbouring_areas(areas)
    return areas


def group_neighbouring_areas(areas):
    previous_areas_count = len(areas)
    while True:
        groups = group_when_any(areas, are_areas_neighbouring)
        areas = [merge_areas(group) for group in groups]
        areas_count = len(areas)
        if areas_count == previous_areas_count:
            return areas
        previous_areas_count = areas_count


def merge_areas(areas):
    return [
        min([area[0] for area in areas]),
        min([area[1] for area in areas]),
        max([area[2] for area in areas]),
        max([area[3] for area in areas]),
    ]


def are_areas_neighbouring(a, b):
    return any(
        (
            b[0] - a[2] == 1 and (0 <= b[1] - a[3] <= 1 or intersects_on_y_axis(a, b)),
            a[0] - b[2] == 1 and (-1 <= a[1] - b[3] <= 1 or intersects_on_y_axis(a, b)),
            b[1] - a[3] == 1 and (0 <= b[0] - a[2] <= 1 or intersects_on_x_axis(a, b)),
            a[1] - b[3] == 1 and ((0 <= a[0] - b[2] <= 1) or intersects_on_x_axis(a, b)),
            intersects_on_x_axis(a, b) and intersects_on_y_axis(a, b),
        )
    )


def intersects_on_x_axis(a, b):
    return (
        a[0] <= b[0] <= a[2] or
        a[0] <= b[2] <= a[2] or
        (b[0] < a[0] and b[2] > a[2])
    )


def intersects_on_y_axis(a, b):
    return (
        a[1] <= b[1] <= a[3] or
        a[1] <= b[3] <= a[3] or
        (b[1] < a[1] and b[3] > a[3])
    )


if __name__ == '__main__':
    image = cv.imread('a5.png')
    image_grayscale = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    areas = detect_objects(image_grayscale)
    plot = image.copy()
    for area in areas:
        cv.rectangle(plot, area[0:2], area[2:4], (0, 0xFF, 0), thickness=1)
    cv.rectangle(plot, area[0:2], area[2:4], (0, 0xFF, 0), thickness=1)
    cv.imshow('Plot', plot)
    cv.waitKey(0)
