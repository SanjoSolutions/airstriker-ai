import retro
from gym.wrappers import ResizeObservation
from retro import Actions
import cv2 as cv
import shutil
import os

from main import detect_objects


def main():
    screenshots_folder_path = 'steps/'
    clean_folder(screenshots_folder_path)

    environment = retro.make(
        game='Airstriker-Genesis'
    )
    full_dimensions = environment.observation_space.shape[0:2]
    environment = ResizeObservation(environment, (37, 53))
    reduced_dimensions = environment.observation_space.shape[0:2]

    ai = AI(environment)

    def translate_position(position):
        return (
            position[0] * (full_dimensions[0] / float(reduced_dimensions[0])),
            position[1] * (full_dimensions[1] / float(reduced_dimensions[1]))
        )

    observations = environment.reset()
    i = 0
    while True:
        action = ai.choose(observations)
        observations, reward, done, info = environment.step(action)
        cv.imwrite(
            screenshots_folder_path + str(i) + '.png',
            cv.cvtColor(observations, cv.COLOR_BGR2RGB)
        )
        i += 1
        environment.render()
        if done:
            environment.reset()


def clean_folder(path):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
    os.mkdir(path)


# ['B', 'A', 'MODE', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'C', 'Y', 'X', 'Z']
idle = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
shoot = (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
left = (0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)
right = (0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0)


asteroid_width = 3
airship_width = 10


class AI:
    def __init__(self, environment):
        self.environment = environment
        self.i = 0

    def choose(self, observations):
        objects = detect_objects(observations)
        if len(objects['airship']):
            airship = objects['airship'][0]
            asteroids = objects['asteroids']
            a = len(asteroids)
            if a >= 1:
                print('a')
            asteroids = list(filter(
                lambda asteroid: asteroid[1] >= self.get_environment_height() * 0.2,
                asteroids
            ))
            if len(asteroids) >= 1:
                print('dodge commando')
                safe_zones = self.determine_safe_zones(asteroids)
                closest_safe_zone = self.determine_closest_safe_zone(safe_zones, airship)
                distance_to_closest_safe_zone = self.distance_to_safe_zone(airship, closest_safe_zone)
                if distance_to_closest_safe_zone > 0:
                    if self.is_airship_to_the_left_of_safe_zone(airship, closest_safe_zone):
                        action = right
                    elif self.is_airship_to_the_right_of_safe_zone(airship, closest_safe_zone):
                        action = left
                    else:
                        action = self.shoot_or_idle()
                else:
                    action = self.shoot_or_idle()
            else:
                action = self.shoot_or_idle()
            self.i += 1
        else:
            cv.imwrite('3.png', observations)
            action = idle
        return action

    def shoot_or_idle(self):
        return shoot if self.i % 8 == 0 else idle

    def determine_safe_zones(self, asteroids):
        asteroids = sorted(asteroids, key=lambda asteroid: asteroid[0])
        safe_zones = []
        index = 0
        asteroid = asteroids[index]
        from_x = (
            0 if self.get_asteroid_left_bound(asteroid) >= 1
            else self.get_asteroid_left_bound(asteroid) - 1
        ) + 0.5 * airship_width
        while from_x < self.get_environment_width() and index < len(asteroids):
            to_x = self.get_asteroid_left_bound(asteroid) - 1 - 0.5 * airship_width
            if from_x < to_x:
                safe_zone = (from_x, to_x)
                safe_zones.append(safe_zone)
            from_x = self.get_asteroid_right_bound(asteroid) + 1 + 0.5 * airship_width
            index += 1
            if index < len(asteroids):
                asteroid = asteroids[index]
        if from_x <= self.get_environment_width() - 1:
            to_x = self.get_environment_width() - 1 - 0.5 * airship_width
            if from_x < to_x:
                safe_zone = (from_x, to_x)
                safe_zones.append(safe_zone)
        return safe_zones

    def determine_closest_safe_zone(self, safe_zones, airship):
        safe_zones = sorted(safe_zones, key=lambda safe_zone: self.distance_to_safe_zone(airship, safe_zone))
        return safe_zones[0]

    def distance_to_safe_zone(self, airship, safe_zone):
        if self.is_airship_to_the_left_of_safe_zone(airship, safe_zone):
            return safe_zone[0] - airship[0]
        elif self.is_airship_to_the_right_of_safe_zone(airship, safe_zone):
            return airship[0] - safe_zone[1]
        else:
            return 0

    def is_airship_to_the_left_of_safe_zone(self, airship, safe_zone):
        return airship[0] < safe_zone[0]

    def is_airship_to_the_right_of_safe_zone(self, airship, safe_zone):
        return airship[0] > safe_zone[1]

    def get_asteroid_left_bound(self, asteroid):
        return asteroid[0] - ((asteroid_width - 1) / 2)

    def get_asteroid_right_bound(self, asteroid):
        return asteroid[0] + ((asteroid_width - 1) / 2)

    def get_environment_width(self):
        return self.environment.observation_space.shape[0]

    def get_environment_height(self):
        return self.environment.observation_space.shape[1]


if __name__ == '__main__':
    main()
