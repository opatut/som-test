#!/usr/bin/env python2

import random, math, time, pygame

def color(vector):
    return tuple([int(c*255) for c in vector.data])


def read_bitmap(filename):
    with open(filename, "rb") as f:
        data = bytearray(f.read())

    bitmap = []
    i = 54
    for y in range(512):
        row = []
        for x in range(512):
            row.append(Node(x, y, [x/255.0 for x in data[i:i+3]]))
            i += 3
        bitmap.append(row)
    return bitmap

def mix(a, b, f):
    return a + (b-a)*f

class Vector(object):
    def __init__(self, *data):
        self.data = data

    def distance(self, other):
        return math.sqrt(sum([pow(self.data[i] - other.data[i], 2) for i in range(len(self.data))]))

    def __repr__(self):
        return "( " + " | ".join(["{:.3f}".format(d) for d in self.data]) + " )"

    def update(self, other, factor):
        self.data = [mix(self.data[i], other.data[i], factor) for i in range(len(self.data))]

    @property
    def x(self): return self.data[0]

    @property
    def y(self): return self.data[1]

    @property
    def z(self): return self.data[2]

class Node(object):
    def __init__(self, x, y, data=[]):
        self.weights = Vector(*data) if data else Vector(*[random.random() for i in range(3)])
        self.position = Vector(x, y)

    def __repr__(self):
        return "Node {position} at {weight}".format(position=self.position, weight=self.weights)

def generate_grid(w, h):
    nodes = []
    for x in range(w):
        for y in range(h):
            nodes.append(Node(1.0*x/(w-1), 1.0*y/(h-1)))
    return nodes

def print_grid(nodes):
    for node in nodes:
        print(node)

def get_bmu(pixel, grid):
    return min(grid, key=lambda node: node.weights.distance(pixel.weights) ) 

def gaussian(center, position, spread):
    return math.exp(- (position.x - center.x)**2 / (2*spread)**2 - (position.y - center.y)**2 / (2*spread)**2 )

def get_neighbourhood_factor(bmu, node, spread):
    return 1 if bmu == node else gaussian(bmu.position, node.position, spread)

if __name__ == "__main__":
    spread = 0.2
    learning_rate = 0.5

    grid = generate_grid(40, 40)
    bitmap = read_bitmap("data/rgb1.bmp")

    pygame.init()
    screen = pygame.display.set_mode((512, 512), 0, 32)

    # iterate, generate the map
    for i in range(2000):
        print("Iteration {} {}".format(i, spread))

        # for row in bitmap:
        #   for pixel in row:
        pixel = random.choice(random.choice(bitmap))

        bmu = get_bmu(pixel, grid)

        screen.fill((0, 0, 0))

        for node in grid:
            f = learning_rate * get_neighbourhood_factor(bmu, node, spread)
            node.weights.update(pixel.weights, f)

            pygame.draw.rect(screen, color(node.weights), (int(node.position.x * 512.0), int(node.position.y * 512.0), 30, 30))

        pygame.display.update()
        pygame.display.flip()

        spread *= 0.997
        learning_rate *= 0.999
        # time.sleep(0.2 * learning_rate)

    # for node in grid: print(node)

    draw(grid)