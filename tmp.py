import math

import numpy as np
from manimlib import *

sys.path.append('/home/ivan/Documents/UCU/DM_2021/Project2')

from organism import Organism, Flower


class Test(Scene):
    def construct(self):
        self.camera.frame.set_height(20)
        a_org = Organism(self)
        a_org.angle = PI
        a_org.coordinates = (99, 99)
        self.camera.frame.move_to(a_org.coordinates[0] * RIGHT +
                                  a_org.coordinates[1] * UP)
        b_org = Organism(self)
        c_org = Flower(self)
        c_org.coordinates = (98, 97)
        c = Circle().move_to(RIGHT * c_org.coordinates[0] +
                             UP * c_org.coordinates[1])
        a = Circle().move_to(RIGHT * a_org.coordinates[0] +
                             UP * a_org.coordinates[1])
        for angle in np.arange(0.0, 2 * PI, 0.5):
            a_org.size = random.random()
            angle += PI
            b_org.coordinates = (4.0 * math.cos(angle) + 100,
                                 4.0 * math.sin(angle) + 100)
            b = Circle().move_to(RIGHT * b_org.coordinates[0] +
                                 UP * b_org.coordinates[1])
            a_org.angle = angle
            self.add(a, b, c)
            self.add(Line(LEFT + DOWN, DOWN + RIGHT*101),
                     Line(LEFT + DOWN, LEFT + UP*101),
                     Line(RIGHT*101 + UP*101, LEFT + UP*101),
                     Line(RIGHT*101 + UP*101, DOWN + RIGHT*101))
            update_views = np.array(
                [[5.0, 0.0]
                 for _ in range(24)]
            )
            a_org.update_view(b_org, update_views)
            a_org.update_view(c_org, update_views)
            a_org.update_walls(update_views)
            lines = []
            for idx in range(24):
                half_angle = (np.pi / 12 + (3 * np.pi / 4 - np.pi / 12)
                              * (1 - a_org.size))
                cur_angle = a_org.angle + half_angle - (half_angle / 11.5) * idx
                vector = UP * math.sin(cur_angle) + RIGHT * math.cos(cur_angle)
                line = Line(a.get_center(),
                            a.get_center() + vector * update_views[idx, 0])
                self.add(line)
            self.wait(1)
            self.clear()
