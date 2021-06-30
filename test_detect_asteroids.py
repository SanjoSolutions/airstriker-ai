import cv2 as cv

from main import detect_objects

test_cases = (
    # id, asteroid count
    (1, 2),
    (2, 2),
    (3, 1)
)


def test_position_detection(id, asteroid_count):
    image = cv.imread('test_detect_asteroids/' + str(id) + '.png')
    objects = detect_objects(image)
    positions = objects['asteroids']
    print(positions)
    assert len(positions) == asteroid_count


for id, asteroid_count in test_cases:
    test_position_detection(id, asteroid_count)
