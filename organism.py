import numpy
from manimlib import *
from constants import *
import random


class Organism:

    def __init__(self, scene, size=None, neural_network: np.ndarray = None,
                 time_appeared=0):
        # self.scene = scene
        self.size = size
        if size is None:
            self.size = round(random.random() * (1 - FLOWER_ENERGY_SCALE) +
                              FLOWER_ENERGY_SCALE, 2)
        self.neural_network = neural_network
        if neural_network is None:
            self.generate_random_network()

        self.ate_amount = 0

        self.energy = BASE_ENERGY
        self.time_lived = 0
        self.coordinates = (
            min(99, round(random.random() * MAX_X_COORD, 2)),
            min(99, round(random.random() * MAX_Y_COORD, 2)))
        self.angle = random.random() * 2 * np.pi

        self.is_alive = True
        self.time_appeared = time_appeared
        # self.__start_data = repr(self)

        # self.obj = scene.new_organism(self)
        # scene.animations[-1].append(FadeIn(self.obj))

    def generate_random_network(self):
        input_hl_weights = np.random.random(size=(INPUT_LAYER,
                                                  HIDDEN_LAYER)) * 2 - 1
        hl_output_weights = np.random.random(size=(HIDDEN_LAYER,
                                                   OUTPUT_LAYER)) * 2 - 1
        self.neural_network = [input_hl_weights.round(2),
                               hl_output_weights.round(2)]

    def handle_collision(self, other):
        dist = np.sqrt((self.coordinates[0] - other.coordinates[0]) ** 2 +
                       (self.coordinates[1] - other.coordinates[1]) ** 2)
        if dist < 2 * RADIUS:
            return self._eat(other)

    def _eat(self, other):
        other: Organism
        if self.size < other.size and not isinstance(other, Flower):
            return other._eat(self)

        other.is_alive = False
        self.ate_amount += 1
        self.energy += other.size * BASE_ENERGY_RECEIVE
        # self.scene.animations[-1].append(FadeOut(other.obj))
        return other

    def make_move(self, eyes_data=None):
        def activation_func(data):
            return (2.0 / (1.0 + numpy.exp(-1 * data))) - 1

        if eyes_data is None:
            eyes_data = np.zeros(EYES_AMOUNT * 2)
        input_data = numpy.append(eyes_data, [self.size, self.energy, 1])
        hidden_layer = numpy.matmul(input_data, self.neural_network[0])
        hidden_layer = activation_func(hidden_layer)
        output_layer = numpy.matmul(hidden_layer, self.neural_network[1])
        velocity, angular = activation_func(output_layer)
        self._make_movement(velocity, angular * MAX_ANGULAR_VELOCITY)

    def _make_movement(self, velocity, angular):
        r = velocity / angular
        circle_center = (
            self.coordinates[0] + numpy.cos(self.angle + numpy.pi / 2) * r,
            self.coordinates[1] + numpy.sin(self.angle + numpy.pi / 2) * r
        )
        self.coordinates = (
            circle_center[0] + numpy.cos(
                self.angle - numpy.pi / 2 + angular) * r,
            circle_center[1] + numpy.sin(
                self.angle - numpy.pi / 2 + angular) * r)
        self.coordinates = (
            round(min(max(self.coordinates[0], 0), MAX_X_COORD), 2),
            round(min(max(self.coordinates[1], 0), MAX_Y_COORD), 2)
        )
        self.angle += angular

        energy_consumed = \
            (BASE_CONSUMPTION +
             MOVEMENT_CONSUMPTION * abs(velocity)) * self.size
        self.energy -= energy_consumed

        self.time_lived += 1

        # self.scene.animations[-1].append(Rotate(
        #     self.obj,
        #     angular,
        #     about_point=UP * circle_center[1] + RIGHT * circle_center[0]
        # ))
        # self.scene.animations[-1].append(self.obj.animate.move_to(
        #     self.coordinates[0] * RIGHT + self.coordinates[1] * UP
        # ))

    def update_view(self, other, view_data):
        import update_views
        half_angle = (MIN_VIEW_ANGLE + (MAX_VIEW_ANGLE -
                                        MIN_VIEW_ANGLE)
                      * (1 - self.size))
        update_views.update_views(self.coordinates, other.coordinates,
                                  view_data,
                                  self.angle + half_angle,
                                  self.angle - half_angle,
                                  other.size)

    def update_walls(self, view_data):
        import update_views
        half_angle = (MIN_VIEW_ANGLE + (MAX_VIEW_ANGLE -
                                        MIN_VIEW_ANGLE)
                      * (1 - self.size))
        update_views.update_view_walls(self.coordinates,
                                       view_data,
                                       self.angle + half_angle,
                                       self.angle - half_angle)

    # def __str__(self):
    #     return self.__start_data

    def __repr__(self):
        return f'{self.time_appeared}, {self.size}, {self.coordinates}, ' \
               f'{self.angle}, {self.energy}, {self.time_lived},    ' \
               f'{{{self.neural_network[0].tolist()}; ' \
               f'{self.neural_network[1].tolist()}}}\n'

    def network_vector(self):
        return numpy.append(self.neural_network[0],
                            self.neural_network[1])

    @classmethod
    def neural_network_from_vector(cls, vector):
        return [vector[:INPUT_LAYER * HIDDEN_LAYER]
                    .reshape((INPUT_LAYER, HIDDEN_LAYER)),
                vector[INPUT_LAYER * HIDDEN_LAYER:]
                    .reshape((HIDDEN_LAYER, OUTPUT_LAYER))]


class Flower(Organism):

    def __init__(self, scene, time_appeared=0):
        super().__init__(scene, FLOWER_ENERGY_SCALE, np.empty(0),
                         time_appeared)

    def __repr__(self):
        return f'{self.time_appeared}, {self.coordinates}\n'

    def __str__(self):
        return f'{self.time_appeared}, {self.coordinates}\n'

    def _eat(self, other):
        other: Organism
        if isinstance(other, Flower):
            return
        else:
            other._eat(self)
