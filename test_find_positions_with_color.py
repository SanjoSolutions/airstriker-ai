import cv2 as cv

from main import find_positions_with_color

image = cv.imread('Screenshot 2021-06-09 at 16.08.33.png')

color_range_enemy_airship = ((0x90, 0x91), (0x10, 0x10), (0x49, 0x4a))
positions = find_positions_with_color(image, color_range_enemy_airship)

print(positions)

image_with_marked_positions = image.copy()
for position in positions:
    x = position[0]
    y = position[1]
    image_with_marked_positions[y, x] = (0x0, 0xFF, 0x0)

cv.imwrite('positions.png', image_with_marked_positions)
cv.imshow('Positions', image_with_marked_positions)
cv.waitKey(0)
