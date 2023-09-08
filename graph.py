import math


class Graph:
    def __init__(self) -> None:
        with open("hypermarket.txt") as f:
            self.map = [[int(num) for num in line.split(" ")] for line in f]
            self.graph, self.coords = self.__build_graph()

    def __build_graph(self):
        coords = {}
        for i, line in enumerate(self.map):
            for j, point in enumerate(line):
                coords[point] = (i, j)
        coords[0] = coords[-1]
        del coords[-1]
        num_of_points = len(coords)
        matrix = [[0] * num_of_points for i in range(num_of_points)]
        for num in range(len(matrix)):
            for key in coords:
                matrix[num][key] = math.sqrt(
                    (coords[num][0] - coords[key][0]) ** 2 + (coords[num][1] - coords[key][1]) ** 2
                )
                if num == key:
                    matrix[num][key] = math.inf
        return matrix, coords

    def __find_min_distance_in_matrix(self, start, goods):
        min_distance = math.inf
        num_of_1st_good = -1
        for good in goods:
            if min_distance > self.graph[0][good]:
                min_distance = self.graph[0][good]
                num_of_1st_good = good
        return num_of_1st_good

    def dijkstra(self, real_goods: list, recommendations: list):
        way = []
        way.append(self.__find_min_distance_in_matrix(0, real_goods))
        real_goods.pop(real_goods.index(way[0]))
        all_goods = real_goods + recommendations
        while len(all_goods) > 0:
            way.append(self.__find_min_distance_in_matrix(way[-1], all_goods))
            all_goods.pop(all_goods.index(way[-1]))
        way =  [-1, *way]
        return way[::-1]


if __name__ == "__main__":
    graph = Graph()
    print(graph.coords)
    print(graph.dijkstra([12, 8], [11, 5]))
