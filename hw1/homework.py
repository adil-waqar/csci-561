from collections import OrderedDict, deque
from heapq import heapify
from queue import PriorityQueue

directions = [
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1)
]


class Node:
    def __init__(self, value, coords) -> None:
        self.value = value
        self.coords = coords
        self.children = []


class Mountain:
    def __init__(self, dim, start, stamina, no_of_lodges, lodges, terrain_map) -> None:
        self.dim = dim
        self.start = start
        self.stamina = stamina
        self.no_of_lodges = no_of_lodges
        self.lodges = lodges
        self.terrain_map = terrain_map

        # create a graph
        self.graph = {}

        for j in range(dim[0]):
            for i in range(dim[1]):
                self.graph[(i, j)] = Node(self.terrain_map[i][j], (i, j))

        for j in range(dim[0]):
            for i in range(dim[1]):
                for k, l in directions:
                    if ((i + k) >= 0 and (j + l) >= 0 and (i + k) <= (dim[1] - 1) and (j + l) <= (dim[0] - 1)):
                        fut_elevation = self.terrain_map[i+k][j+l]
                        curr_elevation = abs(self.terrain_map[i][j])

                        if (fut_elevation < 0 and abs(fut_elevation) <= curr_elevation):
                            self.graph[(i, j)].children.append(
                                (self.graph[(i + k, j + l)], 0))

                        if (fut_elevation >= 0 and fut_elevation <= curr_elevation):
                            self.graph[(i, j)].children.append(
                                (self.graph[(i + k, j + l)], 0))

                        if (fut_elevation >= curr_elevation and fut_elevation - curr_elevation <= stamina):
                            self.graph[(i, j)].children.append(
                                (self.graph[(i + k, j + l)], fut_elevation - curr_elevation))

        self.start_node = self.graph[(self.start[1], self.start[0])]
        self.end_nodes = [self.graph[(y, x)] for x, y in self.lodges]


class MyPriorityQueue(PriorityQueue):
    def change_priority(self, priority, item):
        for index in range(len(self.queue)):
            if (self.queue[index][1] == item):
                if (priority < self.queue[index][0]):
                    self.queue[index] = (priority, item)
                    heapify(self.queue)
                    return True
                else:
                    return False

        return False


def read_input():
    with open("input.txt", "r") as f:
        file = f.read().splitlines()

    search_algo = file[0]
    dim = tuple(int(x) for x in file[1].split(" "))
    start = tuple(int(x) for x in file[2].split(" "))
    stamina = int(file[3])
    no_of_lodges = int(file[4])
    lodges = []

    for line in file[5:no_of_lodges+5]:
        lodges.append(tuple(int(x) for x in line.split(" ")))

    terrain_map = []
    for line in file[no_of_lodges+5:]:
        terrain_map.append([int(x) for x in line.split(" ")])

    return search_algo, Mountain(
        dim=dim,
        start=start,
        stamina=stamina,
        no_of_lodges=no_of_lodges,
        lodges=lodges,
        terrain_map=terrain_map
    )


def bfs(mountain: Mountain):
    start_node = mountain.start_node
    end_nodes = mountain.end_nodes
    paths = OrderedDict()

    for end_node in end_nodes:
        frontier = deque([start_node])
        reached = set([start_node])
        parent = {}

        while len(frontier):
            node = frontier.popleft()
            for child, _ in node.children:
                if child == end_node:
                    path = deque()
                    while parent.get(child):
                        path.appendleft(child.coords)
                        child = parent.get(child)
                    path.appendleft(child.coords)
                    # add path for end_node
                    paths[end_node.coords] = path

                if child not in reached:
                    parent[child] = node
                    reached.add(child)
                    frontier.append(child)

        if paths.get(end_node.coords) is None:
            paths[end_node.coords] = "FAIL"

    return paths


def ucs(mountain: Mountain):
    start_node = mountain.start_node
    end_nodes = mountain.end_nodes
    paths = OrderedDict()

    for end_node in end_nodes:
        frontier = MyPriorityQueue()
        frontier.put(0, start_node)
        reached = set([start_node])
        parent = {}

        while frontier.qsize != 0:
            path_cost, node = frontier.get()
            return True

        return True

    return True


def write_output(solution: OrderedDict):
    lines = []
    for key in solution.keys():
        if solution.get(key) != 'FAIL':
            line = ""
            for x, y in solution.get(key):
                line += f'{y},{x} '
            line += "\n"
            lines.append(line)
        else:
            line = solution.get(key) + "\n"
            lines.append(line)

    with open("output.txt", "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    algo, mountain = read_input()
    paths = bfs(mountain=mountain)
    write_output(paths)
