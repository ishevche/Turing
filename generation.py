import random

import manimlib

import time as tl

import constants
from constants import *
from organism import Organism, Flower


class Generation:
    def __init__(self, scene):
        self.scene = scene
        self.organisms: set[Organism] = set()
        self.flowers: set[Flower] = set()
        self.blocks: list[list[list[Organism]]] = \
            [[list() for _ in range(10)] for _ in range(10)]

        # self.organisms_data = ''
        # self.flowers_data = ''
        self._initialize_flowers(constants.FLOWERS_AMOUNT)

        self.average_lifetimes = []
        self.average_energy = []

    def _initialize_flowers(self, amount, time=9):
        for _ in range(amount):
            flower = Flower(self.scene, time)
            self._add_organism_to_blocks(flower)
            self.flowers.add(flower)
            # self.flowers_data += str(flower)

    def _add_organism_to_blocks(self, organism):
        x_coord = int(organism.coordinates[0] // 10)
        y_coord = int(organism.coordinates[1] // 10)
        self.blocks[x_coord][y_coord].append(organism)
        if (organism.coordinates[0] < (x_coord - 1) * 10 + constants.RADIUS and
                x_coord - 1 > -1):
            self.blocks[x_coord - 1][y_coord].append(organism)
        if (organism.coordinates[0] > (x_coord + 1) * 10 - constants.RADIUS and
                x_coord + 1 < 10):
            self.blocks[x_coord + 1][y_coord].append(organism)
        if (organism.coordinates[1] < (y_coord - 1) * 10 + constants.RADIUS and
                y_coord - 1 > -1):
            self.blocks[x_coord][y_coord - 1].append(organism)
        if (organism.coordinates[1] > (y_coord + 1) * 10 - constants.RADIUS and
                y_coord + 1 < 10):
            self.blocks[x_coord][y_coord + 1].append(organism)

    def _remove_organism_from_blocks(self, organism):
        x_coord = int(organism.coordinates[0] // 10)
        y_coord = int(organism.coordinates[1] // 10)
        self.blocks[x_coord][y_coord].remove(organism)
        if (organism.coordinates[0] < (x_coord - 1) * 10 + constants.RADIUS and
                x_coord - 1 > -1):
            self.blocks[x_coord - 1][y_coord].remove(organism)
        if (organism.coordinates[0] > (x_coord + 1) * 10 - constants.RADIUS and
                x_coord + 1 < 10):
            self.blocks[x_coord + 1][y_coord].remove(organism)
        if (organism.coordinates[1] < (y_coord - 1) * 10 + constants.RADIUS and
                y_coord - 1 > -1):
            self.blocks[x_coord][y_coord - 1].remove(organism)
        if (organism.coordinates[1] > (y_coord + 1) * 10 - constants.RADIUS and
                y_coord + 1 < 10):
            self.blocks[x_coord][y_coord + 1].remove(organism)

    def set_random_population(self, amount):
        for i in range(amount):
            organism = Organism(self.scene)
            self.organisms.add(organism)
            self._add_organism_to_blocks(organism)
            # self.organisms_data += str(organism)

    def add_organisms(self, organisms):
        for organism in organisms:
            self.organisms.add(organism)
            self._add_organism_to_blocks(organism)
            # self.organisms_data += str(organism)

    # def add_mutated(self, amount):
    #     organisms = []
    #     for _ in range(amount):
    #         parent = random.choice(list(self.organisms))
    #         child = self.mutate_from_organism(parent)
    #         organisms.append(child)
    #     self.add_organisms(organisms)

    def mutate_from_organism(self, parent, time=0):
        network_vector = parent.network_vector()
        num_mutations = int(constants.MUTATION_PERCENT *
                            network_vector.size // 100)
        mutation_indices = np.array(
            random.sample(range(network_vector.size), num_mutations))
        random_values = np.random.random(mutation_indices.size) - 0.5
        network_vector[mutation_indices] = (network_vector[mutation_indices] +
                                            random_values)
        new_size = parent.size
        if random.random() < constants.MUTATION_PERCENT / 100:
            new_size += random.random() * 0.4 - 0.2
            new_size = round(min(max(new_size, FLOWER_ENERGY_SCALE), 1), 2)
        network_matrix = Organism.neural_network_from_vector(network_vector)
        for idx, matrix in enumerate(network_matrix):
            network_matrix[idx] = np.round(matrix, 2)
        return Organism(self.scene, new_size, network_matrix, time)

    def run(self, time=-1, path_to_flower_file='flowers.txt',
            path_to_organism_file='organisms.txt',
            path_to_result_file='results.txt'):
        time_passed = 0
        # self.scene.play(*self.scene.animations[-1], run_time=0.05)
        is_not_over = True
        while time != time_passed and self.organisms and \
                len(self.organisms) < 500 and is_not_over:
            try:
                time_passed += 1
                self._move_everyone()
                self._check_collisions(time_passed)
                if time_passed % 10 == 0:
                    self._average_lifetime()
                    self._average_energy()
                    self._born_mutated(time_passed)
                if time_passed % 100 == 0:
                    print(f'{time_passed:5} -> {len(self.organisms):3}, '
                          f'{self.average_lifetimes[-1]} - '
                          f'{self.average_energy[-1]}')
                    # f'{time_for_move:3} = {time_to_move:3} + '
                    # f'{time_to_coli:3} + {time_to_mutate:3}')
                # self.write_down(path_to_organism_file, path_to_flower_file,
                #                 time_passed)
            except KeyboardInterrupt:
                is_not_over = False
        self.write_results(path_to_result_file)
        print(time_passed)

    def _average_lifetime(self):
        self.average_lifetimes.append(
            sum(map(lambda x: x.time_lived,
                    self.organisms)) / len(self.organisms)
        )

    def _average_energy(self):
        self.average_energy.append(
            sum(map(lambda x: x.energy,
                    self.organisms)) / len(self.organisms)
        )

    def _born_mutated(self, time):
        children = []
        for parent in self.organisms:
            if random.random() < parent.ate_amount / BASE_ENERGY:
                parent.energy /= 2
                child = self.mutate_from_organism(parent, time)
                children.append(child)
        self.add_organisms(children)

    def _move_everyone(self):
        remove = set()
        # smallest = sorted(self.organisms, key=lambda x: x.size)[0]
        for organism in self.organisms:
            if not organism.is_alive:
                continue
            view_data = np.array(
                [[constants.VIEW_DISTANCE, 0.0]
                 for _ in range(constants.EYES_AMOUNT)]
            )
            lower_x = (organism.coordinates[0] - constants.VIEW_DISTANCE) // 10
            upper_x = (organism.coordinates[0] + constants.VIEW_DISTANCE) // 10
            lower_y = (organism.coordinates[1] - constants.VIEW_DISTANCE) // 10
            upper_y = (organism.coordinates[1] + constants.VIEW_DISTANCE) // 10
            lower_x = int(max(0, lower_x))
            lower_y = int(max(0, lower_y))
            upper_x = int(min(9, upper_x))
            upper_y = int(min(9, upper_y))
            for i in range(lower_x, upper_x + 1):
                for j in range(lower_y, upper_y + 1):
                    for other in self.blocks[i][j]:
                        if other is organism:
                            continue
                        organism.update_view(other, view_data)
            organism.update_walls(view_data)
            # for other in self.flowers:
            #     if other.is_alive and other is not organism:
            #         organism.update_view(other, view_data)
            # if organism is smallest:
            #     self.play_lines(smallest, view_data)
            self._remove_organism_from_blocks(organism)
            organism.make_move(view_data)
            if organism.energy < 0:
                remove.add(organism)
                organism.is_alive = False
                # self.scene.animations[-1]. \
                #     append(manimlib.FadeOut(organism.obj))
            else:
                self._add_organism_to_blocks(organism)
        # self.play_anim()
        for dead in remove:
            self.organisms.remove(dead)
            del dead

    # def play_lines(self, smallest, smallest_view):
    #     half_angle = (MIN_VIEW_ANGLE + (MAX_VIEW_ANGLE -
    #                                     MIN_VIEW_ANGLE)
    #                   * (1 - smallest.size))
    #     from manimlib import UP, RIGHT, Line, FadeIn, FadeOut
    #     anims = []
    #     post_anims = []
    #     for idx in range(24):
    #         cur_angle = smallest.angle + half_angle - (half_angle / 11.5) * idx
    #         vector = UP * math.sin(cur_angle) + RIGHT * math.cos(cur_angle)
    #         line = Line(smallest.obj.get_center(),
    #                     smallest.obj.get_center() +
    #                     vector * smallest_view[idx, 0])
    #         anims.append(FadeIn(line))
    #         post_anims.append(FadeOut(line))
    #     self.scene.play(*anims, self.scene.camera
    #                     .frame.animate.move_to(smallest.obj),
    #                     run_time=0.000000001)
    #     self.scene.wait(0.01)
    #     self.scene.play(*post_anims, run_time=0.000000001)

    # def play_anim(self):
    #     self.scene.play(*self.scene.animations[-1], run_time=0.000000001)
    #     self.scene.next_move_setup()

    def _check_collisions(self, time):
        flowers_to_spawn = 0
        for row in range(10):
            for col in range(10):
                for org1 in self.blocks[row][col]:
                    for org2 in self.blocks[row][col]:
                        if org1 is org2:
                            continue
                        dead = org1.handle_collision(org2)
                        if dead is None:
                            continue
                        self._remove_organism_from_blocks(dead)
                        if isinstance(dead, Flower):
                            flowers_to_spawn += 1
                            self.flowers.remove(dead)
                        else:
                            self.organisms.remove(dead)
                        if dead is org1:
                            del dead
                            break
                        del dead
        self._initialize_flowers(flowers_to_spawn, time)

    def write_down(self, organisms, flowers, time):
        with open(organisms, 'a') as organisms_output:
            data = f'{time}:'
            for organism in self.organisms:
                data += f'{organism.coordinates};'
            data += '\n'
            organisms_output.write(data)
        with open(flowers, 'a') as flowers_output:
            data = f'{time}:'
            for flower in self.flowers:
                data += f'{flower.coordinates};'
            data += '\n'
            flowers_output.write(data)

    def write_results(self, path):
        with open(path, 'w') as output:
            data = ':=-organisms-=:\n'
            for organism in self.organisms:
                data += organism.__repr__()
            data += ':=-flowers-=:\n'
            for flower in self.flowers:
                data += repr(flower)

            output.write(data)
            output.write(', '.join(map(str, self.average_energy)) + '\n')
            output.write(', '.join(map(str, self.average_lifetimes)) + '\n')
