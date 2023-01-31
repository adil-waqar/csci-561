from collections import OrderedDict, deque
from heapq import heapify
from math import sqrt
from queue import PriorityQueue

directions = {
    (-1, 0): 10,
    (-1, 1): 14,
    (0, 1): 10,
    (1, 1): 14,
    (1, 0): 10,
    (1, -1): 14,
    (0, -1): 10,
    (-1, -1): 14
}


class Node:
    def __init__(self, value, coords) -> None:
        self.value = value
        self.coords = coords
        self.momentum = 0
        self.children = []

    def __lt__(self, _):
        return True


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
                for k, l in directions.keys():
                    if ((i + k) >= 0 and (j + l) >= 0 and (i + k) <= (dim[1] - 1) and (j + l) <= (dim[0] - 1)):
                        fut_elevation = self.terrain_map[i+k][j+l]
                        curr_elevation = abs(self.terrain_map[i][j])

                        if (not (fut_elevation < 0 and abs(fut_elevation) > curr_elevation)):
                            self.graph[(i, j)].children.append(
                                (self.graph[(i + k, j + l)], directions.get((k, l))))

        self.start_node = self.graph[(self.start[1], self.start[0])]
        self.end_nodes = [self.graph[(y, x)] for x, y in self.lodges]

    def calculate_heuristics(self):
        self.heuristics = {}
        for end_node in self.end_nodes:
            self.heuristics[end_node] = {}
            for coords, _ in self.graph.items():
                self.heuristics[end_node][coords] = round(
                    sqrt(
                        pow(10 * coords[0] - 10 * end_node.coords[0], 2) +
                        pow(10 * coords[1] - 10 * end_node.coords[1], 2))
                )


class MyPriorityQueue(PriorityQueue):
    def change_priority(self, item, priority, actual_cost=0):
        for index in range(len(self.queue)):
            if actual_cost:
                if (self.queue[index][2] == item):
                    if (priority < self.queue[index][0] or (
                            priority == self.queue[index][0] and actual_cost < self.queue[index][1])):
                        self.queue[index] = (priority, actual_cost, item)
                        heapify(self.queue)
                        return True
            else:
                if (self.queue[index][1] == item):
                    if (priority < self.queue[index][0]):
                        self.queue[index] = (priority, item)
                        heapify(self.queue)
                        return True
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

                elevation = abs(child.value) - abs(node.value)
                if child not in reached and elevation <= mountain.stamina:
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
        frontier.put((0, start_node))
        reached = set([start_node])
        parent = {}

        while frontier.qsize() != 0:
            node_path_cost, node = frontier.get()

            if node == end_node:
                path = deque()
                while (parent.get(node)):
                    path.appendleft(node.coords)
                    node = parent.get(node)
                path.appendleft(node.coords)
                # add path for end_node
                paths[end_node.coords] = path

            for child, cost in node.children:
                child_path_cost = node_path_cost + cost
                elevation = abs(child.value) - abs(node.value)
                if child not in reached and elevation <= mountain.stamina:
                    parent[child] = node
                    reached.add(child)
                    frontier.put((child_path_cost, child))
                else:
                    if frontier.change_priority(child, child_path_cost):
                        parent[child] = node

        if paths.get(end_node.coords) is None:
            paths[end_node.coords] = "FAIL"

    return paths


def a_star(mountain: Mountain):
    start_node = mountain.start_node
    end_nodes = mountain.end_nodes
    paths = OrderedDict()

    for end_node in end_nodes:
        frontier = MyPriorityQueue()
        frontier.put((0, 0, start_node))
        reached = set([start_node])
        parent = {}

        while frontier.qsize() != 0:
            _, node_path_cost, node = frontier.get()

            if node == end_node:
                path = deque()
                while (parent.get(node)):
                    path.appendleft(node.coords)
                    node = parent.get(node)
                path.appendleft(node.coords)
                # add path for end_node
                paths[end_node.coords] = path

            for child, cost in node.children:
                child_path_cost = node_path_cost + cost + \
                    mountain.heuristics[end_node][child.coords]

                if child not in reached and is_valid_move(child, node, mountain.stamina):
                    parent[child] = node
                    child.momentum = max(0, abs(node.value) - abs(child.value))
                    child_path_cost += calc_elevation_cost(child, node)
                    reached.add(child)
                    frontier.put(
                        (child_path_cost, node_path_cost + cost, child))
                else:
                    if frontier.change_priority(child, child_path_cost, node_path_cost + cost):
                        parent[child] = node

        if paths.get(end_node.coords) is None:
            paths[end_node.coords] = "FAIL"

    return paths


def is_valid_move(child: Node, parent: Node, stamina):
    curr_elevation = abs(parent.value)
    future_elevation = abs(child.value)

    if (curr_elevation >= future_elevation):
        return True
    if (curr_elevation < future_elevation and curr_elevation + stamina + parent.momentum >= future_elevation):
        return True

    return True


def calc_elevation_cost(child: Node, parent: Node):
    curr_elevation = abs(parent.value)
    future_elevation = abs(child.value)

    if curr_elevation >= future_elevation:
        return 0
    else:
        return future_elevation - curr_elevation - parent.momentum


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
    func_map = {
        "BFS": bfs,
        "UCS": ucs,
        "A*": a_star
    }

    if algo == "A*":
        mountain.calculate_heuristics()

    paths = func_map.get(algo)(mountain)
    write_output(paths)
