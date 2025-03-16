from Pyro4 import expose
import time
import random


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.workers = workers  
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        print("Initialized")

    @staticmethod
    def get_random_graph(n, value_range=(1, 10), inf=9999):
        graph = [[(random.randint(*value_range) if i != j else 0) for j in range(n)] for i in range(n)]
        return graph

    def solve(self):
        print("Job Started")
        n = self.read_input()
        graph = self.get_random_graph(n)
        start_time = time.time()
        result = self.workers[0].floyd_warshall(graph).value  
        total_time = time.time() - start_time

        self.write_output(result, total_time, n)
        print("Job Finished in {:.2f} seconds".format(total_time))


    @staticmethod
    @expose
    def floyd_warshall(graph):
        n = len(graph)
        dist = [row[:] for row in graph]  
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        return dist

    def read_input(self):
        with open(self.input_file_name, 'r') as f:
            n = int(f.readline().strip())
        return n

    def write_output(self, dist, total_time, n):
        with open(self.output_file_name, 'w') as f:
            f.write("\nRegular mode\n")
            f.write("Graph size: {}\n".format(n))
            f.write("Total computation time:" + str(total_time) + "seconds\n")
            for row in dist:
                f.write(' '.join(map(str, row)) + '\n')
        print("Output written to", self.output_file_name)
