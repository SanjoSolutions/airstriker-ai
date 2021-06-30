import retro
import tensorflow as tf
from gym.wrappers import ResizeObservation
from keras.layers import Flatten, Lambda
from retro import RetroEnv, Actions
from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Conv2D, Dense
import numpy as np
from math import floor


def main():
    environment = retro.make(
        game='Airstriker-Genesis',
        use_restricted_actions=Actions.DISCRETE
    )
    environment = ResizeObservation(environment, (53, 37))
    model = Sequential([
        Conv2D(
            # input_shape=environment.observation_space.shape,
            filters=16,
            kernel_size=(8, 8),
            strides=4,
            activation='relu',
            kernel_initializer=tf.keras.initializers.Zeros(),
        ),
        Conv2D(
            filters=32,
            kernel_size=(4, 4),
            strides=2,
            activation='relu',
            kernel_initializer=tf.keras.initializers.Zeros(),
        ),
        Flatten(),
        Dense(
            units=256,
            activation='relu',
            kernel_initializer=tf.keras.initializers.Zeros(),
        ),
        Dense(
            units=environment.action_space.n,
            kernel_initializer=tf.keras.initializers.Zeros()
        ),
    ])
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.MeanSquaredError(),
    )

    observations = environment.reset()
    previous_info = None
    X = []
    Y = []
    n = 0
    while True:
        if n == 1000:
            print('n == 1000')
        if n < 1000:
            action = environment.action_space.sample()
        else:
            model_action = model(np.array([observations], dtype=np.float32))
            action = tf.math.argmax(model_action[0])
        n += 1
        observations, reward, done, info = environment.step(action)
        # objects = detect_objects(observations)
        if previous_info and info['lives'] < previous_info['lives']:
            reward -= 1000 * (previous_info['lives'] - info['lives'])
        environment.render()
        a = np.zeros(environment.action_space.n)
        a[action] = reward  # TODO: Check if indexing works with tensor
        X.append(observations)
        Y.append(a)
        if len(X) >= 32:
            Y2 = np.zeros_like(Y)
            for index in range(len(Y) - 1, 0, -1):
                for index2 in range(index, 0, -1):
                    Y2[index2] += Y[index]
            X = np.array(X, dtype=np.float32)
            Y2 = np.array(Y2, dtype=np.float32)
            model.fit(X, Y2)
            X = []
            Y = []
        previous_info = info
        if done:
            environment.reset()
            previous_info = None


def detect_objects(observations):
    objects = dict()

    # #76789c
    # #76789c
    airship_pattern = (
        np.array(
            (
                ((0x9c, 0x78, 0x76),),
            )
        ),
        np.array(
            (
                ((0x9c, 0x78, 0x76),),
            )
        )
    )
    objects['airship'] = find_positions_with_pattern(observations, airship_pattern)

    enemy_airship_pattern = (
        np.array(
            (
                ((0x49, 0x10, 0x90),),
            )
        ),
        np.array(
            (
                ((0x4a, 0x10, 0x91),),
            )
        )
    )
    objects['enemy_airships'] = find_positions_with_pattern(observations, enemy_airship_pattern)

    green_ball_pattern = (
        np.array(
            (
                ((0x26, 0x5a, 0x10),),
            )
        ),
        np.array(
            (
                ((0x26, 0x5a, 0x10),),
            )
        )
    )
    objects['green_balls'] = find_positions_with_pattern(observations, green_ball_pattern)

    # #696a76
    # #595981
    #
    # #797b7d
    # #4d4d71
    #
    # #6c6d6c
    # #5a5b82
    #
    # #797a7c
    # #4e4e73
    #
    # #6c6d6c
    # #5a5b82
    #
    # #797a7c
    # #4e4e73
    # BGR
    asteroid_pattern = (
        np.array(
            (
                ((0x69, 0x6a, 0x69),),
                ((0x67, 0x49, 0x48),)
            )
        ),
        np.array(
            (
                ((0x87, 0x7f, 0x7e),),
                ((0x85, 0x5e, 0x5d),),
            )
        )
    )
    objects['asteroids'] = find_positions_with_pattern(observations, asteroid_pattern)

    return objects


def find_positions_with_pattern(observations, pattern):
    pattern_width = pattern[0].shape[1]
    pattern_height = len(pattern)
    positions = []
    for y in range(observations.shape[0] - (pattern_width - 1)):
        for x in range(observations.shape[1] - (pattern_height - 1)):
            if does_match_pattern(observations, (x, y), pattern):
                centered_position = center_position((x, y), pattern_width, pattern_height)
                positions.append(centered_position)

    return positions


def center_position(position, pattern_width, pattern_height):
    return (
        position[0] + floor(0.5 * pattern_width),
        position[1] + floor(0.5 * pattern_height)
    )


def does_match_pattern(observations, position, pattern):
    x = position[0]
    y = position[1]

    min_colors = pattern[0]
    max_colors = pattern[1]

    pattern_width = min_colors.shape[1]
    pattern_height = min_colors.shape[0]

    for oy in range(pattern_height):
        for ox in range(pattern_width):
            min_color = min_colors[oy, ox]
            max_color = max_colors[oy, ox]
            color = observations[y + oy, x + ox]
            matches_color = (
                min_color[0] <= color[0] <= max_color[0] and
                min_color[1] <= color[1] <= max_color[1] and
                min_color[2] <= color[2] <= max_color[2]
            )
            if not matches_color:
                return False

    return True


def find_positions_with_color(observations, color_range):
    positions = []
    for y in range(observations.shape[0]):
        for x in range(observations.shape[1]):
            if does_color_match(observations[y, x], color_range):
                positions.append((x, y))

    return positions


# color in BGR
# color_range in RGB
def does_color_match(color, color_range):
    return (
        color_range[0][0] <= color[2] <= color_range[0][1] and
        color_range[1][0] <= color[1] <= color_range[1][1] and
        color_range[2][0] <= color[0] <= color_range[2][1]
    )


if __name__ == '__main__':
    main()
