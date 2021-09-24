from queue import PriorityQueue
import multiprocessing as mp


def divide_vertexes(num_of_vertices, n):
    vertexes = list(range(0, num_of_vertices))
    for i in range(0, len(vertexes), n):
        yield vertexes[i:i + n]


def merge_two_dicts(x, y):
    z = x.copy()   # start with keys and values of x
    z.update(y)    # modifies z with keys and values of y
    return z


def get_min_vertex(d):
    val = min(filter(None, d.values()))
    res = next(k for k, v in d.items() if v == val)
    return res


def get_min_edge_from_source_nodes(edges, source_nodes, des_node):
    if des_node in source_nodes:
        return 0

    min = 999
    for node in source_nodes:
        if edges[node][des_node] != -1:
            distance = edges[node][des_node]
            if distance < min:
                min = distance
    if min == 999:
        min = 0

    return min


temp_results = {}
results = [0]


def handle_on_each_process(vertexes_queue, edges, source_nodes):
    base_queue = {}
    for vertex in vertexes_queue:
        base_queue[vertex] = 0
    for neighbor in vertexes_queue:
        base_queue[neighbor] = get_min_edge_from_source_nodes(
            edges, source_nodes, neighbor)
    min_vertex = get_min_vertex(base_queue)
    return {min_vertex: base_queue[min_vertex]}


def collect_result(result):
    global temp_results
    temp_results = merge_two_dicts(temp_results, result)


class Graph:
    def __init__(self, num_of_vertices):
        self.v = num_of_vertices
        self.edges = [[-1 for i in range(num_of_vertices)]
                      for j in range(num_of_vertices)]
        self.visited = []

    def dijkstra(self, start_vertex):
        D = {v: float('inf') for v in range(self.v)}
        D[start_vertex] = 0

        result = []
        # source_nodes = [start_vertex]
        result.append(start_vertex)

        # Divide vertexes into groups
        # [[0, 1, 2], [3, 4, 5, 6]]
        vertex_queues = list(divide_vertexes(self.v, 3))

        pool = mp.Pool(2)
        global results
        global temp_results
        check_pool_processes_finished_arr = []
        # Go through all vertexes
        while not len(results) >= self.v:
            # Each process will handle a group of vertexes
            for vertexes_queue in vertex_queues:
                result = pool.apply_async(handle_on_each_process, args=(
                    vertexes_queue, self.edges, results), callback=collect_result)
                check_pool_processes_finished_arr.append(result)

            [result.wait() for result in check_pool_processes_finished_arr]
            print('TEMP RESULTS: ', temp_results)
            # Find out the minimum of smallest values of processes
            min_vertex = get_min_vertex(temp_results)
            # Added minimum vertex to result array
            results.append(min_vertex)
            # source_nodes.append(min_vertex)
            temp_results = {}
            # print("SOURCE: ", source_nodes)
            print("RESULTS:", results)

        pool.close()
        pool.join()

        return D

    def add_edge(self, u, v, weight):
        self.edges[u][v] = weight
        self.edges[v][u] = weight


g = Graph(7)
g.add_edge(0, 1, 4)
g.add_edge(0, 6, 7)
g.add_edge(1, 6, 11)
g.add_edge(1, 2, 9)
g.add_edge(2, 3, 6)
g.add_edge(2, 4, 2)
g.add_edge(3, 5, 10)
g.add_edge(4, 5, 1)
g.add_edge(4, 6, 20)
g.add_edge(5, 6, 1)

D = g.dijkstra(0)

# for vertex in range(len(D)):
#     print("Distance from vertex 0 to vertex", vertex, "is", D[vertex])
